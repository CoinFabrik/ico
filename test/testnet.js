const config = require('../config.js');
const assertFail = require('./helpers/assertFail');

const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
// const FlatPricing = artifacts.require('./FlatPricing.sol');
// const BonusFinalizeAgent = artifacts.require('./BonusFinalizeAgent.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol');
// const FixedCeiling = artifacts.require('./FixedCeiling.sol');
// const Crowdsale = artifacts.require('./Crowdsale.sol');
const HubiiCrowdsale = artifacts.require('./HubiiCrowdsale.sol');
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

async function block_await(targetBlock) {
    const actualBlock = await web3.eth.getBlock("latest").number;
    if (actualBlock < targetBlock) {
        return delay_promise(1000).then(block_await(targetBlock));
    } else {
        return actualBlock;
    }
}

contract('Crowdsale', function(accounts) {
    const investmentPerAccount = {};
    for (let i = 0; i < accounts.length; i++) {
        investmentPerAccount[accounts[i]] = web3.toBigNumber(0);
    }

    const GAS = 300000;
    const GAS_PRICE = 20000000000;
    const decimals = 15;
    const tokensInWei = 10 ** 15; 
    const chunkedWeiMultiple = 18000 * (10 ** 18);
    const limitPerAddress = web3.toBigNumber(web3.fromWei(100000 * (10 ** 18)));
    const bonusBasePoints = 3000;

    const exampleAddress0 = accounts[0];
    const exampleAddress1 = accounts[1];
    const exampleAddress2 = accounts[2];
    const exampleAddress3 = accounts[3];

    let rpcId = 2000;

    let crowdsaleToken;
    let crowdsale;
    
    const init_prom = MultiSigWallet.deployed()
    .then(function(instance){
        multiSigWallet = instance;})
    .then(function(){
        return HubiiCrowdsale.deployed();})
    .then(function(instance) {
        console.log("CROWDSALE ADDRESS: ", instance.address);
        crowdsale = instance;
        return crowdsale.token();})
    .then(function(tokenAddress) {
        return CrowdsaleToken.at(tokenAddress);})
    .then(function(tokenInstance){
        crowdsaleToken = tokenInstance;
    });

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
                await delay_promise(1000);
                const transaction = await web3.eth.getTransaction(txHash);
                if (transaction["blockNumber"] != null) {
                    await async_call(web3.currentProvider.sendAsync, { method: "debug_traceTransaction", params: [txHash, {}], jsonrpc: "2.0", id: rpcId}).then(function (response) {
                        let lastOperationIndex = response["result"]["structLogs"].length-1;
                        if (expectedResult == "failure") {
                            assert.notEqual(response["result"]["structLogs"][lastOperationIndex]["error"], null, "Transaction expected to succeed failed 🗙 ");
                        } else if (expectedResult == "success") {
                            assert.equal(response["result"]["structLogs"][lastOperationIndex]["error"], null, "Transaction expected to fail succeeded 🗙 ");
                        }
                    }).catch(function(error) {
                        console.log('UNEXPECTED ERROR <- "handled by mineTransaction", handle in function in order to trace error. 🗙 ');
                        console.log(error);
                    });
                    rpcId = rpcId + 1;
                    console.log("Awaited approximately", iteration,  "seconds until mined 🔨",);
                    return txHash;
                } else {
                    return start(iteration + 1);
                }
            } else
                throw "TRANSACTION WAS NOT MINED 🗙 ";
        };
        return start(0);
    };

   
    it_synched('Checks contract\'s health', async function() {
        assert(await crowdsale.isFinalizerSane());
    });

    it_synched('Checks that nobody can buy before the sale starts', async function() {
        let state = await crowdsale.getState();
        let actualBlock = await web3.eth.getBlock("latest").number;
        let startBlock = await crowdsale.startsAt();
        
        if (actualBlock < startBlock - 2) {
            await mineTransaction({"etherToSend":1, "sender":exampleAddress1, "operation":crowdsale.buy, "expectedResult":"failure"});
        } else {
            console.log("⇩⇩⇩ NOT TESTED BECAUSE OF BEING IN FUNDING STATE⇩⇩⇩");
        }
    });

    it_synched('Waits until the start of the ICO, buys, and checks that tokens belong to new owner', async function() {
        let startBlock = await crowdsale.startsAt();
        await block_await(startBlock).then(async function() {
            const block = await web3.eth.getBlock("latest").number;
            let etherToSend = 3;
            await mineTransaction({"etherToSend":etherToSend, "sender":exampleAddress1, "operation":crowdsale.buy, "expectedResult":"success"});
            const balance = await crowdsaleToken.balanceOf(exampleAddress1);
            investmentPerAccount[exampleAddress1] = investmentPerAccount[exampleAddress1].plus(etherToSend);
            let expectedBalance = web3.toBigNumber(10**decimals*web3.toWei(etherToSend)).dividedBy(tokensInWei);
            console.log("EL BALANCE: ", balance.toNumber());
            console.log("EL ESPERADO: ", expectedBalance.toNumber());
            assert.isTrue(balance.equals(expectedBalance));
            let investorCount = await crowdsale.investorCount();
            assert.isTrue(investorCount.equals(1));
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
        assert.isTrue(web3.fromWei(totalCollected).equals(investmentPerAccount[exampleAddress1].plus(etherToSend)));
        const balanceContributionWallet = await web3.eth.getBalance(multiSigWallet.address);
        assert.isTrue(web3.fromWei(balanceContributionWallet).equals(investmentPerAccount[exampleAddress1].plus(etherToSend)));
        investmentPerAccount[exampleAddress1] = investmentPerAccount[exampleAddress1].plus(etherToSend);

    });   

    it_synched('Checks that customers can buy using its id', async function() {
        let etherToSend = 1;
        let id = 123;
        await mineTransaction({"etherToSend":etherToSend, "sender":exampleAddress2, "operation":crowdsale.buyWithCustomerId, "expectedResult":"success", "id":id});

        const balance = await crowdsaleToken.balanceOf(exampleAddress2);
        investmentPerAccount[exampleAddress2] = investmentPerAccount[exampleAddress2].plus(etherToSend);
        let expectedBalance = web3.toBigNumber(10**decimals*web3.toWei(etherToSend)).dividedBy(tokensInWei);
        assert.isTrue(balance.equals(expectedBalance));
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
        investmentPerAccount[exampleAddress2] = investmentPerAccount[exampleAddress2].plus(etherToSend);
        const collectedAfter = await crowdsale.weiRaised();
        assert.isTrue(web3.fromWei(collectedBefore).lessThan(web3.fromWei(collectedAfter)));
    });

    it_synched('Check transfers failure before tokens are released', async function() {
        await mineTransaction({"operation":crowdsaleToken.transfer, "sender":exampleAddress1, "tokensToSend":1, "receiver":exampleAddress2, "expectedResult":"failure"});
    });

    it_synched('Sets funding cap', async function() {
        let initialFundingCap = await crowdsale.weiFundingCap();
        assert.isTrue(web3.fromWei(initialFundingCap).equals(180000));
        let weiRaised = await crowdsale.weiRaised();
        let newFundingCap = weiRaised.plus(initialFundingCap).dividedBy(chunkedWeiMultiple).floor().plus(1).times(chunkedWeiMultiple).plus(initialFundingCap);
        await mineTransaction({"operation":crowdsale.setFundingCap, "newFundingCap":newFundingCap.toNumber(), "expectedResult":"success"});
        let finalFundingCap = await crowdsale.weiFundingCap();
        assert.isTrue(finalFundingCap.equals(newFundingCap));
    });

    it_synched('Checks state after all tokens have been sold to multiple accounts', async function() {
        let fundingCap = await crowdsale.weiFundingCap();
        let actualWeiRaised = await crowdsale.weiRaised();
        let remaining = fundingCap.minus(actualWeiRaised);
        while (actualWeiRaised.lessThan(fundingCap)) {
            randomAccountIndex = Math.round((Math.random() * (accounts.length-2)) + 1);
            // randomInvestment = Math.floor((Math.random() * (limitPerAddress-1)) + 1);
            randomInvestment = limitPerAddress.minus(1).times(Math.random().toPrecision(15) ).plus(1).floor();
            if (investmentPerAccount[accounts[randomAccountIndex]].greaterThanOrEqualTo(limitPerAddress)) {
                continue;
            } else {
                let addressLimitedInvestment = limitPerAddress.minus(investmentPerAccount[accounts[randomAccountIndex]]);
                let capLimitedInvestment =  web3.fromWei(fundingCap.minus(actualWeiRaised));
                // let effectiveInvestment = Math.min(addressLimitedInvestment, capLimitedInvestment, randomInvestment);
                let effectiveInvestment = web3.BigNumber.min(addressLimitedInvestment, capLimitedInvestment, randomInvestment);
                await mineTransaction({"etherToSend":randomInvestment, "sender":accounts[randomAccountIndex], "operation":crowdsale.buy, "expectedResult":"success"});
                
                investmentPerAccount[accounts[randomAccountIndex]] = investmentPerAccount[accounts[randomAccountIndex]].plus(effectiveInvestment);
                investedAmount = await crowdsale.investedAmountOf(accounts[randomAccountIndex]);
                assert.isTrue(web3.fromWei(investedAmount).equals(investmentPerAccount[accounts[randomAccountIndex]]));
            }
            actualWeiRaised = await crowdsale.weiRaised();
        } 

        let finalWeiRaised = await crowdsale.weiRaised();

        assert.isTrue(finalWeiRaised.equals(fundingCap));
        assert.isFalse(await crowdsaleToken.released());
        state = await crowdsale.getState();
        assert.isTrue(state.equals(3)); // Checks if state is Success

        await mineTransaction({"operation":crowdsale.finalize, "expectedResult":"success"});

        const tokensSold = await crowdsale.tokensSold();
        const teamFinalBalance = await crowdsaleToken.balanceOf(multiSigWallet.address);
        const expectedMWBalance = tokensSold.times(bonusBasePoints).dividedBy(10000 - bonusBasePoints).floor();
        assert.isTrue(teamFinalBalance.equals(expectedMWBalance));

        assert.isTrue(await crowdsale.finalized());
        assert.isTrue(await crowdsaleToken.released());

        const initialBalance0 = await crowdsaleToken.balanceOf(exampleAddress0);
        assert.isTrue(initialBalance0.equals(0));

        const tokensToSend = 1;
        await mineTransaction({"operation":crowdsaleToken.transfer, "sender":exampleAddress1, "tokensToSend":tokensToSend, "receiver":exampleAddress0, "expectedResult":"success"});

        const finalBalance0 = await crowdsaleToken.balanceOf(exampleAddress0);
        assert.isTrue(finalBalance0.equals(tokensToSend));
    });
});