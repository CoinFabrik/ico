const config = require('../config.js');
const assertFail = require('./helpers/assertFail');

const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const FlatPricing = artifacts.require('./FlatPricing.sol');
const BonusFinalizeAgent = artifacts.require('./BonusFinalizeAgent.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol');
const FixedCeiling = artifacts.require('./FixedCeiling.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');
const iterationLimit = 120;

function delay_promise(delay) {
    return new Promise(function(resolve, reject) {
        setTimeout(function() { resolve(); }, delay);
    });
}

const callbackGenerator = function (resolve, reject) {
    return function (error, value) {
        if (error) {
            reject(error);
        } else {
            resolve(value);
        }
    };
};

// Promisify a web3 asynchronous call (this becomes unnecessary as soon as web3 promisifies its API)
function async_call(method, ...args) {
    return new Promise(function (resolve, reject) {
        method(...args, callbackGenerator(resolve, reject));
    });
}

contract('Crowdsale', function(accounts) {
    const investmentPerAccount = {};
    for (let i = 0; i < accounts.length; i++) {
        investmentPerAccount[accounts[i]] = 0;
    }

    const GAS = 300000;
    const GAS_PRICE = 20000000000;

    const exampleAddress0 = accounts[0];
    const exampleAddress1 = accounts[1];
    const exampleAddress2 = accounts[2];
    const exampleAddress3 = accounts[3];

    let rpcId = 2000;

    let crowdsaleToken;
    let flatPricing;
    let multiSigWallet;
    let fixedCeiling;
    let crowdsale;
    let bonusFinalizeAgent;
    const init_prom = Promise.all([ CrowdsaleToken.deployed().then(function(instance) {crowdsaleToken = instance}),
                                  FlatPricing.deployed().then(function(instance) {flatPricing = instance}),
                                  MultiSigWallet.deployed().then(function(instance) {multiSigWallet = instance}),
                                  FixedCeiling.deployed().then(function(instance) {fixedCeiling = instance}),
                                  Crowdsale.deployed().then(function(instance) {crowdsale = instance}),
                                  BonusFinalizeAgent.deployed().then(function(instance) {bonusFinalizeAgent = instance}) 
                                ]);
    let promise_chain = init_prom;

    // Error logging handled by mocha/chai
    const it_synched = function(message, test_f) {
        it(message, function() {
            this.timeout(0);
            promise_chain = promise_chain.then(test_f);
            return promise_chain;
        });
    }

    async function mineTransaction({operation, sender, etherToSend, newFundingCap, receiver, tokensToSend, expectedResult, id}) {
        let txHash;
        if (operation == crowdsale.buy) {
            txHash = await operation.sendTransaction({value: web3.toWei(etherToSend), gas: GAS, gasPrice: GAS_PRICE, from: sender});
        } else if (operation == crowdsale.buyWithCustomerId) {
            txHash = await operation.sendTransaction(id, {value: web3.toWei(etherToSend), gas: GAS, gasPrice: GAS_PRICE, from: sender});
        } else if (operation == crowdsale.halt || operation == crowdsale.unhalt || operation == crowdsale.finalize) {
            return operation();
        } else if (operation == crowdsale.setFundingCap) {
            return operation(newFundingCap);
        } else if (operation == crowdsaleToken.transfer) {
            txHash = await operation.sendTransaction(receiver, tokensToSend, {from: sender});
        } else {
            throw "Operation not supported";
        }

        async function start(iteration) {
            if (iteration < iterationLimit) {//check "once per second"
                await delay_promise(1000).then(async function() {
                    const transaction = await web3.eth.getTransaction(txHash);
                    if (transaction["blockNumber"] != null) {
                        await async_call(web3.currentProvider.sendAsync, { method: "debug_traceTransaction", params: [txHash, {}], jsonrpc: "2.0", id: rpcId}).then(function (response) {
                            let lastOperationIndex = response["result"]["structLogs"].length-1;
                            if (expectedResult == "failure") {
                                assert.notEqual(response["result"]["structLogs"][lastOperationIndex]["error"], null, "Transaction expected to succeed failed 🗙");
                            } else if (expectedResult == "success") {
                                assert.equal(response["result"]["structLogs"][lastOperationIndex]["error"], null, "Transaction expected to fail succeeded 🗙");
                            }
                        }).catch(function(error) {
                            console.log("UNEXPECTED ERROR <- \"handled by mineTransaction\", handle in function in order to trace error. 🗙");
                            console.log(error);
                        });
                        rpcId = rpcId + 1;
                        console.log("Awaited iterations until mined 🔨: ", iteration);
                        return txHash;
                    } else {
                        return start(iteration + 1);
                    }
                });
            } else
                throw "TRANSACTION WAS NOT MINED 🗙";
        };
        return start(0);
    };

   
    it_synched('Checks contract\'s health', async function() {
        assert(await crowdsale.isFinalizerSane() && await crowdsale.isPricingSane() && await crowdsale.isCeilingSane());
        // console.log(Date.now()/1000 | 0);
    });

    it_synched('Checks that nobody can buy before the sale starts', async function() {
        let state = await crowdsale.getState();
        let actualTime = new Date().getTime();
        let startDate = await crowdsale.startsAt();
        
        if (actualTime < startDate.toNumber() * 1000) {
            await mineTransaction({"etherToSend":1, "sender":exampleAddress1, "operation":crowdsale.buy, "expectedResult":"failure"});
        } else {
            console.log("⇩⇩⇩ NOT TESTED BECAUSE OF BEING IN FUNDING STATE⇩⇩⇩");
        }
    });

    it_synched('Waits until the start of the ICO, buys, and checks that tokens belong to new owner', async function() {
        let startTime = await crowdsale.startsAt();
        let timeDelta = startTime * 1000 - (new Date().getTime()); 
        await delay_promise(Math.max(timeDelta, 10)).then(async function() {
            let etherToSend = 3;
            await mineTransaction({"etherToSend":etherToSend, "sender":exampleAddress1, "operation":crowdsale.buy, "expectedResult":"success"});
            const balance = await crowdsaleToken.balanceOf(exampleAddress1);    
            investmentPerAccount[exampleAddress1] += etherToSend;
            assert.equal(web3.fromWei(balance).toNumber(), (etherToSend * (10 ** config.decimals)) / web3.toWei(config.price));
            let investorCount = await crowdsale.investorCount();
            assert.equal(investorCount.toNumber(), 1);
        });
    });


    it_synched('Checks that ether goes where it should after a purchase', async function() {
        const initialBalance = await web3.eth.getBalance(exampleAddress1);
        let etherToSend = 2;
        let txHash = await mineTransaction({"etherToSend":etherToSend, "sender":exampleAddress1, "operation":crowdsale.buy, "expectedResult":"success"});

        const finalBalance = await web3.eth.getBalance(exampleAddress1);
        const spent = web3.fromWei(initialBalance.sub(finalBalance)).toNumber();
        tx_receipt = await web3.eth.getTransactionReceipt(txHash);

        const expected_gas_usage = parseFloat(web3.fromWei(tx_receipt.gasUsed * GAS_PRICE));
        const expected_spent = etherToSend + parseFloat(web3.fromWei(tx_receipt.gasUsed * GAS_PRICE));
        const gas_used = parseFloat(web3.fromWei(tx_receipt.gasUsed * GAS_PRICE));
        const totalCollected = await crowdsale.weiRaised();
        assert.equal(web3.fromWei(totalCollected).toNumber(), investmentPerAccount[exampleAddress1] + etherToSend);
        const balanceContributionWallet = await web3.eth.getBalance(multiSigWallet.address);
        assert.equal(web3.fromWei(balanceContributionWallet).toNumber(), investmentPerAccount[exampleAddress1] + etherToSend);
        investmentPerAccount[exampleAddress1] += etherToSend;
    });   

    it_synched('Checks that customers can buy using its id', async function() {
        let etherToSend = 1;
        let id = 123;
        await mineTransaction({"etherToSend":etherToSend, "sender":exampleAddress2, "operation":crowdsale.buyWithCustomerId, "expectedResult":"success", "id":id});

        const balance = await crowdsaleToken.balanceOf(exampleAddress2);
        investmentPerAccount[exampleAddress2] += etherToSend;
        assert.equal(web3.fromWei(balance).toNumber(), (investmentPerAccount[exampleAddress2] * (10 ** config.decimals)) / web3.toWei(config.price));
    });


    it_synched('Pauses and resumes the contribution', async function() {
        let etherToSend = 1;
        await mineTransaction({"operation":crowdsale.halt, "expectedResult":"success"}); 
        assert.isTrue(await crowdsale.halted());
        await mineTransaction({"etherToSend":etherToSend, "sender":exampleAddress2, "operation":crowdsale.buy, "expectedResult":"failure"});

        await mineTransaction({"operation":crowdsale.unhalt, "expectedResult":"success"});
        assert.isFalse(await crowdsale.halted());

        const collectedBefore = await crowdsale.weiRaised();
        await mineTransaction({"etherToSend":etherToSend, "sender":exampleAddress2, "operation":crowdsale.buy, "expectedResult":"success"});
        
        investmentPerAccount[exampleAddress2] += etherToSend;
        const collectedAfter = await crowdsale.weiRaised();
        assert.isBelow(web3.fromWei(collectedBefore).toNumber(), web3.fromWei(collectedAfter).toNumber());
    });

    it_synched('Check transfers failure before tokens are released', async function() {
        await mineTransaction({"operation":crowdsaleToken.transfer, "sender":exampleAddress1, "tokensToSend":1, "receiver":exampleAddress2, "expectedResult":"failure"});
    });

    it_synched('Sets funding cap', async function() {
        let initialFundingCap = await crowdsale.weiFundingCap();
        assert.equal(initialFundingCap, 0);

        let weiRaised = await crowdsale.weiRaised();
        weiRaised = weiRaised.toNumber();
        let chunkedWeiMultiple = parseInt(web3.toWei(config.chunkedMultipleCap));
        let newFundingCap = (Math.trunc(weiRaised / chunkedWeiMultiple) + 1) * chunkedWeiMultiple;
        await mineTransaction({"operation":crowdsale.setFundingCap, "newFundingCap":newFundingCap, "expectedResult":"success"});
        let finalFundingCap = await crowdsale.weiFundingCap();
        assert.equal(finalFundingCap.toNumber(), newFundingCap);
    });

    it_synched('Checks state after all tokens have been sold to multiple accounts', async function() {
        let fundingCap = await crowdsale.weiFundingCap();
        fundingCap = fundingCap.toNumber();
        let actualWeiRaised = await crowdsale.weiRaised();
        actualWeiRaised = actualWeiRaised.toNumber();
        let remaining = fundingCap - actualWeiRaised;
        while (actualWeiRaised < fundingCap) {
            randomAccountIndex = Math.round((Math.random() * (accounts.length-2)) + 1);
            randomInvestment = Math.floor((Math.random() * (config.limitPerAddress-1)) + 1);
            if (investmentPerAccount[accounts[randomAccountIndex]] >= config.limitPerAddress) {
                continue;
            } else {
                let addressLimitedInvestment = config.limitPerAddress - investmentPerAccount[accounts[randomAccountIndex]];
                let capLimitedInvestment =  web3.fromWei(fundingCap) - web3.fromWei(actualWeiRaised);
                let effectiveInvestment = Math.min(addressLimitedInvestment, capLimitedInvestment, randomInvestment);
  
                await mineTransaction({"etherToSend":randomInvestment, "sender":accounts[randomAccountIndex], "operation":crowdsale.buy, "expectedResult":"success"});
                
                investmentPerAccount[accounts[randomAccountIndex]] += effectiveInvestment;
                investedAmount = await crowdsale.investedAmountOf(accounts[randomAccountIndex]);
                assert.equal(web3.fromWei(investedAmount).toNumber(), investmentPerAccount[accounts[randomAccountIndex]]);
            }
            actualWeiRaised = await crowdsale.weiRaised();
            actualWeiRaised = actualWeiRaised.toNumber();
        } 

        let finalWeiRaised = await crowdsale.weiRaised();

        assert.equal(finalWeiRaised.toNumber(), fundingCap);
        assert.isFalse(await crowdsaleToken.released());
        state = await crowdsale.getState();
        assert.equal(state.toNumber(), 4); // Checks if state is Success

        await mineTransaction({"operation":crowdsale.finalize, "expectedResult":"success"});

        const tokensSold = await crowdsale.tokensSold();
        const teamFinalBalance = await crowdsaleToken.balanceOf(multiSigWallet.address);
        
        assert.equal(teamFinalBalance.toNumber(), Math.floor(tokensSold.toNumber() * config.bonusBasePoints / 10000));
        assert.isTrue(await crowdsale.finalized());
        assert.isTrue(await crowdsaleToken.released());

        const initialBalance0 = await crowdsaleToken.balanceOf(exampleAddress0);
        assert.equal(initialBalance0.toNumber(), 0);

        const tokensToSend = 1;
        await mineTransaction({"operation":crowdsaleToken.transfer, "sender":exampleAddress1, "tokensToSend":tokensToSend, "receiver":exampleAddress0, "expectedResult":"success"});

        const finalBalance0 = await crowdsaleToken.balanceOf(exampleAddress0);
        assert.equal(finalBalance0.toNumber(), tokensToSend);
    });
});