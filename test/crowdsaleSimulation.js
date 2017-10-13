const config = require('../config.js')(web3);

const advanceBlock = require('./helpers/advanceBlock');
const advanceToBlock = require('./helpers/advanceToBlock');
const latestBlockTime = require('./helpers/latestBlockTime');
const TokenTranchePricing = artifacts.require("../contracts/TokenTranchePricing.sol");

const durations = require('./helpers/durations');
const seconds = durations.seconds;
const minutes = durations.minutes;
const hours = durations.hours;

const increaseTime = require('./helpers/increaseTime').increaseTime;
const increaseTimeTo = require('./helpers/increaseTime').increaseTimeTo;

const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');



const BigNumber = web3.BigNumber;

require('chai')
  .use(require('chai-as-promised'))
  .use(require('chai-bignumber')(BigNumber))
  .should();

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

  async function timestamp_await(target_timestamp) {
    const actual_timestamp = await web3.eth.getBlock("latest").timestamp;
    if (actual_timestamp < target_timestamp) {
      return delay_promise((target_timestamp - actual_timestamp)*1000).then(timestamp_await(target_timestamp));
    } else {
      return actual_timestamp;
    }
  }


contract('Crowdsale', function(accounts) {
  const investmentPerAccount = {};
  for (let i = 0; i < accounts.length; i++) {
    investmentPerAccount[accounts[i]] = web3.toBigNumber(0);
  }

  const GAS = 300000;
  const GAS_PRICE = 20000000000;
  const decimals = 18;
  // const tokensInWei = 10 ** 15; 

  let rpcId = 2000;

  let crowdsaleToken;
  let crowdsale;
  let mulisigwallet;

  const init_prom = MultiSigWallet.deployed()
  .then(function(instance){
    multiSigWallet = instance;})
  .then(function(){
    return Crowdsale.deployed();})
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
    } else if (operation == crowdsale.setEarlyParticipantWhitelist) {
      return operation(receiver, true);
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

   
  it_synched("Checks that nobody can buy before the pre-ico starts", async function() {
    let actualDate = await web3.eth.getBlock("latest").number;
    let startDate = await crowdsale.startsAt();
    if (actualDate + minutes(5) < startDate) {
      await mineTransaction({"etherToSend":3, "sender":accounts[1], "operation":crowdsale.buy, "expectedResult":"failure"});
      (await crowdsaleToken.balanceOf(accounts[1])).should.be.bignumber.and.equal(0);
      await mineTransaction({"operation":crowdsale.setEarlyParticipantWhitelist, "receiver": accounts[1]});
      await mineTransaction({"etherToSend":3, "sender":accounts[0], "operation":crowdsale.buy, "expectedResult":"failure"});
    } else {
      console.log("Not tested because of start date been passed");
    }
  });


  it_synched("Checks that whitelisted early investors can buy during pre-ico", async function() {
    let start_date = await crowdsale.startsAt();
    await timestamp_await(start_date);
    let etherToSend = 3;
    await mineTransaction({"etherToSend":etherToSend, "sender":accounts[1], "operation":crowdsale.buy, "expectedResult":"success"});
    investmentPerAccount[accounts[1]] = investmentPerAccount[accounts[1]].plus(etherToSend);
    const balance = await crowdsaleToken.balanceOf(accounts[1]);
    assert.isTrue(balance.greaterThan(0));
    (await crowdsale.investorCount()).should.be.bignumber.and.equal(1);

    // let expectedBalance = web3.toBigNumber(10**decimals*web3.toWei(etherToSend)).dividedBy(tokensInWei);
  });
  
  it_synched("Checks that non-whitelisted investors cannot buy during pre-ico", async function() {
    const initial_investor_count = await crowdsale.investorCount();
    const initial_balance = await crowdsaleToken.balanceOf(accounts[2]);
    let actualDate = await web3.eth.getBlock("latest").number;
    await mineTransaction({"etherToSend":3, "sender":accounts[2], "operation":crowdsale.buy, "expectedResult":"failure"});
    // await crowdsaleToken.balanceOf((accounts[2])).should.be.bignumber.and.equal(initial_balance);
    (await crowdsale.investorCount()).should.be.bignumber.and.equal(initial_investor_count);
  });

  it_synched("Checks that no one can buy between pre-ico's end and ico's start", async function() {
    const initial_investor_count = await crowdsale.investorCount();
    const initial_balance = await crowdsaleToken.balanceOf(accounts[2]);
    await timestamp_await(config.pre_ico_tranches_end + seconds(30));

    let etherToSend = 3;
    await mineTransaction({"etherToSend":etherToSend, "sender":accounts[2], "operation":crowdsale.buy, "expectedResult":"failure"});
    (await crowdsaleToken.balanceOf(accounts[2])).should.be.bignumber.and.equal(initial_balance);
    (await crowdsale.investorCount()).should.be.bignumber.and.equal(initial_investor_count);
  });



  // it_synched('Checks that ether goes where it should after a purchase', async function() {
    
  //   timestamp_await(config.ico_tranches_start);

  //   const initial_bbalance = await web3.eth.getBalance(accounts[1]);
    
  //   let etherToSend = 2;
    
  //   let txHash = await mineTransaction({"etherToSend":etherToSend, "sender":accounts[1], "operation":crowdsale.buy, "expectedResult":"success"});
    
  //   const finalBalance = await web3.eth.getBalance(accounts[1]);
    
  //   const spent = web3.fromWei(initial_balance.sub(finalBalance)).toNumber();
    
  //   tx_receipt = await web3.eth.getTransactionReceipt(txHash);

  //   const expected_gas_usage = parseFloat(web3.fromWei(tx_receipt.gasUsed * GAS_PRICE));
    
  //   const expected_spent = etherToSend + parseFloat(web3.fromWei(tx_receipt.gasUsed * GAS_PRICE));
    
  //   const gas_used = parseFloat(web3.fromWei(tx_receipt.gasUsed * GAS_PRICE));
    
  //   const total_collected = await crowdsale.weiRaised();
    
  //   assert.isTrue(web3.fromWei(total_collected).equals(investmentPerAccount[accounts[1]].plus(etherToSend)));
    
  //   const balanceContributionWallet = await web3.eth.getBalance(multiSigWallet.address);
    
  //   assert.isTrue(web3.fromWei(balanceContributionWallet).equals(investmentPerAccount[accounts[1]].plus(etherToSend)));
    
  //   investmentPerAccount[accounts[1]] = investmentPerAccount[accounts[1]].plus(etherToSend);

  // });

  // it_synched('Checks that customers can buy using its id', async function() {
  //   let etherToSend = 1;
  //   let id = 123;
  //   await mineTransaction({"etherToSend":etherToSend, "sender":accounts[2], "operation":crowdsale.buyWithCustomerId, "expectedResult":"success", "id":id});

  //   const balance = await crowdsaleToken.balanceOf(accounts[2]);
  //   investmentPerAccount[accounts[2]] = investmentPerAccount[accounts[2]].plus(etherToSend);
  //   let expectedBalance = web3.toBigNumber(10**decimals*web3.toWei(etherToSend)).dividedBy(tokensInWei);
  //   assert.isTrue(balance.equals(expectedBalance));
  // });


  // it_synched('Pauses and resumes the contribution', async function() {
  //   let etherToSend = 1;
  //   await mineTransaction({"operation":crowdsale.halt, "expectedResult":"success"});
  //   assert.isTrue(await crowdsale.halted());
  //   await mineTransaction({"etherToSend":etherToSend, "sender":accounts[2], "operation":crowdsale.buy, "expectedResult":"failure"});

  //   await mineTransaction({"operation":crowdsale.unhalt, "expectedResult":"success"});
  //   assert.isFalse(await crowdsale.halted());

  //   const collectedBefore = await crowdsale.weiRaised();
  //   await mineTransaction({"etherToSend":etherToSend, "sender":accounts[2], "operation":crowdsale.buy, "expectedResult":"success"});
  //   investmentPerAccount[accounts[2]] = investmentPerAccount[accounts[2]].plus(etherToSend);
  //   const collectedAfter = await crowdsale.weiRaised();
  //   assert.isTrue(web3.fromWei(collectedBefore).lessThan(web3.fromWei(collectedAfter)));
  // });

  // it_synched('Check transfers failure before tokens are released', async function() {
  //   await mineTransaction({"operation":crowdsaleToken.transfer, "sender":accounts[1], "tokensToSend":1, "receiver":accounts[2], "expectedResult":"failure"});
  // });


  // it_synched('Checks state after all tokens have been sold to multiple accounts', async function() {
  //   let fundingCap = await crowdsale.weiFundingCap();
  //   let actualWeiRaised = await crowdsale.weiRaised();
  //   let remaining = fundingCap.minus(actualWeiRaised);
  //   while (actualWeiRaised.lessThan(fundingCap)) {
  //     randomAccountIndex = Math.round((Math.random() * (accounts.length-2)) + 1);
  //     // randomInvestment = Math.floor((Math.random() * (limitPerAddress-1)) + 1);
  //     randomInvestment = limitPerAddress.minus(1).times(Math.random().toPrecision(15) ).plus(1).floor();
  //     if (investmentPerAccount[accounts[randomAccountIndex]].greaterThanOrEqualTo(limitPerAddress)) {
  //       continue;
  //     } else {
  //       let addressLimitedInvestment = limitPerAddress.minus(investmentPerAccount[accounts[randomAccountIndex]]);
  //       let capLimitedInvestment =  web3.fromWei(fundingCap.minus(actualWeiRaised));
  //       // let effectiveInvestment = Math.min(addressLimitedInvestment, capLimitedInvestment, randomInvestment);
  //       let effectiveInvestment = web3.BigNumber.min(addressLimitedInvestment, capLimitedInvestment, randomInvestment);
  //       await mineTransaction({"etherToSend":randomInvestment, "sender":accounts[randomAccountIndex], "operation":crowdsale.buy, "expectedResult":"success"});
        
  //       investmentPerAccount[accounts[randomAccountIndex]] = investmentPerAccount[accounts[randomAccountIndex]].plus(effectiveInvestment);
  //       investedAmount = await crowdsale.investedAmountOf(accounts[randomAccountIndex]);
  //       assert.isTrue(web3.fromWei(investedAmount).equals(investmentPerAccount[accounts[randomAccountIndex]]));
  //     }
  //     actualWeiRaised = await crowdsale.weiRaised();
  //   } 

  //   let finalWeiRaised = await crowdsale.weiRaised();

  //   assert.isTrue(finalWeiRaised.equals(fundingCap));
  //   assert.isFalse(await crowdsaleToken.released());
  //   state = await crowdsale.getState();
  //   assert.isTrue(state.equals(3)); // Checks if state is Success

  //   await mineTransaction({"operation":crowdsale.finalize, "expectedResult":"success"});

  //   const tokensSold = await crowdsale.tokensSold();
  //   const teamFinalBalance = await crowdsaleToken.balanceOf(multiSigWallet.address);
  //   const expectedMWBalance = tokensSold.times(bonusBasePoints).dividedBy(10000 - bonusBasePoints).floor();
  //   assert.isTrue(teamFinalBalance.equals(expectedMWBalance));

  //   assert.isTrue(await crowdsale.finalized());
  //   assert.isTrue(await crowdsaleToken.released());

  //   const initialBalance0 = await crowdsaleToken.balanceOf(accounts[0]);
  //   assert.isTrue(initialBalance0.equals(0));

  //   const tokensToSend = 1;
  //   await mineTransaction({"operation":crowdsaleToken.transfer, "sender":accounts[1], "tokensToSend":tokensToSend, "receiver":accounts[0], "expectedResult":"success"});

  //   const finalBalance0 = await crowdsaleToken.balanceOf(accounts[0]);
  //   assert.isTrue(finalBalance0.equals(tokensToSend));
  // });
});