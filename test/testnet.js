const config = require('../config.js');
const assertFail = require('./helpers/assertFail');

const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const FlatPricing = artifacts.require('./FlatPricing.sol');
const BonusFinalizeAgent = artifacts.require('./BonusFinalizeAgent.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol');
const FixedCeiling = artifacts.require('./FixedCeiling.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');
var index = 0;
var timeoutLimit = 120;

contract('Crowdsale', function(accounts) {
    var investmentPerAccount = {};  
    for (var i = 0; i < accounts.length; i++) {
        investmentPerAccount[accounts[i]] = 0;
    }

    const GAS = 300000;
    const GAS_PRICE = 20000000000;

    const exampleAddress0 = accounts[0];
    const exampleAddress1 = accounts[1];
    const exampleAddress2 = accounts[2];
    const exampleAddress3 = accounts[3];

    var rpcId = 2000;

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

    async function mineTransaction(params) {
        let operation = params.operation; 
        let sender = params.sender; 
        let etherToSend = params.etherToSend; 
        let newFundingCap = params.newFundingCap; 
        let receiver = params.receiver; 
        let tokensToSend = params.tokensToSend; 
        let expectedResult = params.expectedResult; 
        let id = params.id;
        switch(operation) {
            case crowdsale.buy:
                txHash = await operation.sendTransaction({value: web3.toWei(etherToSend), gas: GAS, gasPrice: GAS_PRICE, from: sender});
                break;
            case crowdsale.buyWithCustomerId:
                txHash = await operation.sendTransaction(id, {value: web3.toWei(etherToSend), gas: GAS, gasPrice: GAS_PRICE, from: sender});
                break;
            case crowdsale.halt:
                txHash = await operation();
                return;
            case crowdsale.unhalt:
                txHash = await operation();
                return;
            case crowdsale.finalize:
                txHash = await operation();
                return;
            case crowdsale.setFundingCap:
                txHash = await operation(newFundingCap);
                return;
            case crowdsaleToken.transfer:
                txHash = await operation.sendTransaction(receiver, tokensToSend, {from: sender});
                break;
            default:
                throw "Operation not expected";
        }

        async function start(counter) {
            if(counter < timeoutLimit) {
                await new Promise(function(resolve, reject) { 
                setTimeout(
                    async function() {
                        const transaction = await web3.eth.getTransaction(txHash);
                        if(transaction["blockNumber"] != null) {
                            let tx_receipt = await web3.eth.getTransactionReceipt(txHash);
                            await new Promise( (internalResolve, internalReject) => {
                                web3.currentProvider.sendAsync({ method: "debug_traceTransaction", params: [txHash, {}], jsonrpc: "2.0", id: rpcId}, function (err, response) { 
                                    if(!err) {
                                        let lastOperationIndex = response["result"]["structLogs"].length-1;
                                        if(expectedResult == "failure") {
                                            assert.notEqual(response["result"]["structLogs"][lastOperationIndex]["error"], null, "Transaction succeeded although failure expected 🗙");
                                        } else if(expectedResult == "success") {
                                            assert.equal(response["result"]["structLogs"][lastOperationIndex]["error"], null, "Transaction failed despite succeeding was expected 🗙");
                                        }
                                        internalResolve();
                                        resolve();
                                    } else {
                                        console.log("UNEXPECTED ERROR <- \"handled by mineTransaction\", handle in function in order to trace error. 🗙");
                                        console.log(err);
                                        internalReject();
                                        reject(); 
                                    }
                                });
                            });
                            rpcId = rpcId + 1;
                            console.log("Awaited seconds until mined 🔨: ", counter);
                        } else {
                            counter++;
                            await start(counter);
                            resolve();
                            return;
                        }
                    }
                , 1000); //check "once per second"
                })  
            } else if (counter == timeoutLimit) {
                throw "TRANSACTION WAS NOT MINED 🗙";
            } else {
                console.log("STUCK IN THE LIMBO 🌈");
            }
        };
        var counter = 0;
        await start(counter);
    };

   
    it_synched('Checks contract\'s health', async function() {
        assert(await crowdsale.isFinalizerSane() && await crowdsale.isPricingSane() && await crowdsale.isCeilingSane());
        // console.log(Date.now()/1000 | 0);
    });

    it_synched('Checks that nobody can buy before the sale starts', async function() {
        let state = await crowdsale.getState();
        let actualTime = Date.now();
        let startDate = await crowdsale.startsAt();
        
        if (actualTime < startDate.toNumber() * 1000) {
            await mineTransaction({"etherToSend":1, "sender":exampleAddress1, "operation":crowdsale.buy, "expectedResult":"failure"});
        } else {
            console.log("⇩⇩⇩ NOT TESTED BECAUSE OF BEING IN FUNDING STATE⇩⇩⇩");
        }
    });

    it_synched('Waits until the start of the ICO, buys, and checks that tokens belong to new owner', async function() {
        let startTime = await crowdsale.startsAt();
        let timeDelta = startTime * 1000 - Date.now(); 
        await new Promise(function(resolve, reject) { 
            setTimeout(async function() {
                let etherToSend = 3;
                await mineTransaction({"etherToSend":etherToSend, "sender":exampleAddress1, "operation":crowdsale.buy, "expectedResult":"success"});
                const balance = await crowdsaleToken.balanceOf(exampleAddress1);    
                investmentPerAccount[exampleAddress1] += etherToSend;
                assert.equal(web3.fromWei(balance).toNumber(), (etherToSend * (10 ** config.decimals)) / web3.toWei(config.price));
                let investorCount = await crowdsale.investorCount();
                assert.equal(investorCount.toNumber(), 1);
                resolve();
            }, Math.max(timeDelta, 10)); 
        });
    });


    it_synched('Checks that ether goes where it should after a purchase', async function() {
        const initialBalance = await web3.eth.getBalance(exampleAddress1);
        let etherToSend = 2;
        await mineTransaction({"etherToSend":etherToSend, "sender":exampleAddress1, "operation":crowdsale.buy, "expectedResult":"success"});

        const finalBalance = await web3.eth.getBalance(exampleAddress1);
        const spent = web3.fromWei(initialBalance.sub(finalBalance)).toNumber();
        tx_receipt = await web3.eth.getTransactionReceipt(txHash);

        const expected_gas_usage = parseFloat(web3.fromWei(tx_receipt.gasUsed * GAS_PRICE));
        const expected_spent = etherToSend + parseFloat(web3.fromWei(tx_receipt.gasUsed * GAS_PRICE));
        const gas_used = parseFloat(web3.fromWei(tx_receipt.gasUsed * GAS_PRICE));
        const totalCollected = await crowdsale.weiRaised();
        assert.equal(web3.fromWei(totalCollected).toNumber(), investmentPerAccount[exampleAddress1] + etherToSend, "SE ROMPIO TODO 2<<---------");
        const balanceContributionWallet = await web3.eth.getBalance(multiSigWallet.address);
        assert.equal(web3.fromWei(balanceContributionWallet).toNumber(), investmentPerAccount[exampleAddress1] + etherToSend, "SE ROMPIO TODO 3<<---------");
        investmentPerAccount[exampleAddress1] += etherToSend;
    });   

    it_synched('Checks that customers can buy using its id', async function() {
        let etherToSend = 1;
        let id = 123;
        await mineTransaction({"etherToSend":etherToSend, "sender":exampleAddress2, "operation":crowdsale.buyWithCustomerId, "expectedResult":"success", "id":id});


        const balance = await crowdsaleToken.balanceOf(exampleAddress2);
        investmentPerAccount[exampleAddress2] += etherToSend;
        assert.equal(web3.fromWei(balance).toNumber(), ( (investmentPerAccount[exampleAddress2]) * (10 ** config.decimals)) / web3.toWei(config.price));
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

    it_synched('Checks state after all tokens been sold to multiple accounts', async function() {

        let fundingCap = await crowdsale.weiFundingCap();
        fundingCap = fundingCap.toNumber();
        let actualWeiRaised = await crowdsale.weiRaised();
        actualWeiRaised = actualWeiRaised.toNumber();
        let remaining = fundingCap - actualWeiRaised;
        while(actualWeiRaised < fundingCap) {
            randomAccountIndex = Math.round((Math.random() * (accounts.length-2)) + 1);
            randomInvestment = Math.floor((Math.random() * (config.limitPerAddress-1)) + 1);
            if(investmentPerAccount[accounts[randomAccountIndex]] >= config.limitPerAddress) {
                continue;
            } else{
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
        
        assert.equal(teamFinalBalance.toNumber(), Math.floor(tokensSold.toNumber() * config.bonusBasePoints / 10000)); //Solidity truncates non-literal divisions.
        assert.isTrue(await crowdsale.finalized());
        assert.isTrue(await crowdsaleToken.released());

        let initialBalance0 = await crowdsaleToken.balanceOf(exampleAddress0);
        assert.equal(initialBalance0.toNumber(), 0);

        const tokensToSend = 1;
        await mineTransaction({"operation":crowdsaleToken.transfer, "sender":exampleAddress1, "tokensToSend":tokensToSend, "receiver":exampleAddress0, "expectedResult":"success"});

        let finalBalance0 = await crowdsaleToken.balanceOf(exampleAddress0);
        finalBalance0 = finalBalance0.toNumber();
        assert.equal(finalBalance0, tokensToSend);
    });
});