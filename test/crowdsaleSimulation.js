const config = require('../config.js')(web3, "notLiveNet");

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


const amount_offset = 0; 
const start_offset = 1;
const end_offset = 2;
const price_offset = 3;


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

  async function block_await(target_block) {
    const actualBlock = await web3.eth.getBlock("latest").number;
    if (actualBlock < target_block) {
      await delay_promise(1000);
      return block_await(target_block);
    } else {
      return actualBlock;
    }
  }

  async function timestamp_await(target_timestamp) {
    const actual_timestamp = await web3.eth.getBlock("latest").timestamp;
    if (actual_timestamp < target_timestamp) {
      await delay_promise(5*1000);
      return timestamp_await(target_timestamp);
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
  .then(function(instance) {
    multiSigWallet = instance;})
  .then(function() {
    return Crowdsale.deployed();})
  .then(function(instance) {
    console.log("CROWDSALE ADDRESS: ", instance.address);
    crowdsale = instance;
    return crowdsale.token();})
  .then(function(tokenAddress) {
    return CrowdsaleToken.at(tokenAddress);})
  .then(function(tokenInstance) {
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
        const tx_receipt = await web3.eth.getTransactionReceipt(txHash);
          if (expectedResult == "failure") {
            // After out of band discussion with Vitalik and others, I've amended this proposal to simply insert a 1 byte return status (1 for success, 0 for failure).
            assert.equal(tx_receipt["status"], 0, "Transaction expected to fail succeeded 🗙 ");
          } else if (expectedResult == "success") {
            assert.equal(tx_receipt["status"], 1, "Transaction expected to succeed failed 🗙 ");
          }
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
    await mineTransaction({"operation":crowdsale.setEarlyParticipantWhitelist, "receiver": accounts[1]});
    const actual_date = await web3.eth.getBlock("latest").timestamp;
    const first_tranche = await crowdsale.tranches(0);
    if (actual_date + minutes(1) < first_tranche[start_offset].toNumber()) {
      await mineTransaction({"etherToSend":3, "sender":accounts[0], "operation":crowdsale.buy, "expectedResult":"failure"});
      await mineTransaction({"etherToSend":3, "sender":accounts[1], "operation":crowdsale.buy, "expectedResult":"failure"});
      (await crowdsaleToken.balanceOf(accounts[0])).should.be.bignumber.and.equal(0);
      (await crowdsaleToken.balanceOf(accounts[1])).should.be.bignumber.and.equal(0);
    } else {
      console.log("Not tested because of start date been passed");
    }
  });


  it_synched("Checks that whitelisted early investors can buy during pre-ico", async function() {
    const first_tranche = await crowdsale.tranches(0);
    const actual_date_X = await web3.eth.getBlock("latest").timestamp;
    const actual_date = await timestamp_await(first_tranche[start_offset].toNumber());
    if (actual_date > first_tranche[start_offset].toNumber() && actual_date + minutes(1) < first_tranche[end_offset].toNumber()) {
      const etherToSend = 3;
      await mineTransaction({"etherToSend":etherToSend, "sender":accounts[1], "operation":crowdsale.buy, "expectedResult":"success"});
      investmentPerAccount[accounts[1]] = investmentPerAccount[accounts[1]].plus(etherToSend);
      const balance = await crowdsaleToken.balanceOf(accounts[1]);
      assert.isTrue(balance.greaterThan(0));
      (await crowdsale.investorCount()).should.be.bignumber.and.equal(1);
    } else {
      console.log("Not tested because of pre-ico passed");
    }
    // let expectedBalance = web3.toBigNumber(10**decimals*web3.toWei(etherToSend)).dividedBy(tokensInWei);
  });
  
  it_synched("Checks that non-whitelisted investors cannot buy during pre-ico", async function() {
    const initial_investor_count = await crowdsale.investorCount();
    const initial_balance = await crowdsaleToken.balanceOf(accounts[2]);
    const first_tranche = await crowdsale.tranches(0);
    const actual_date = await web3.eth.getBlock("latest").timestamp;
    if (actual_date + minutes(1) < first_tranche[end_offset].toNumber()) {
      await mineTransaction({"etherToSend":3, "sender":accounts[2], "operation":crowdsale.buy, "expectedResult":"failure"});
      (await crowdsaleToken.balanceOf((accounts[2]))).should.be.bignumber.and.equal(initial_balance);
      (await crowdsale.investorCount()).should.be.bignumber.and.equal(initial_investor_count);
    } else {
      console.log("Not tested because of missing pre-ico");
    }
  });

  it_synched("Checks that no one can buy between pre-ico's end and ico's start", async function() {
    const initial_investor_count = await crowdsale.investorCount();
    const initial_balance = await crowdsaleToken.balanceOf(accounts[2]);
    const first_tranche = await crowdsale.tranches(0);
    const second_tranche = await crowdsale.tranches(1);
    const actual_date = await timestamp_await(first_tranche[end_offset].toNumber());
    if (actual_date > first_tranche[end_offset].toNumber() && actual_date + minutes(1) < second_tranche[start_offset].toNumber()) {
      await mineTransaction({"etherToSend":3, "sender":accounts[2], "operation":crowdsale.buy, "expectedResult":"failure"});
      (await crowdsale.investorCount()).should.be.bignumber.and.equal(initial_investor_count);
      (await crowdsaleToken.balanceOf(accounts[2])).should.be.bignumber.and.equal(initial_balance);
    } else {
      console.log("Something gone wrong");
    }
  });

  it_synched('Checks that ether goes where it should after a purchase', async function() {
    const second_tranche = await crowdsale.tranches(1);
    const start_date = await crowdsale.startsAt();
    // console.log("START:", second_tranche[start_offset].toNumber());

    const actual_date = await timestamp_await(second_tranche[start_offset].toNumber());
    const another_actual_date = await timestamp_await(start_date);
    assert.isTrue(another_actual_date >= actual_date);
    // console.log(actual_date);
    if (actual_date + minutes(1) < second_tranche[end_offset].toNumber()) {
      const initial_balance = await web3.eth.getBalance(accounts[1]);
      const etherToSend = 2;
      let txHash = await mineTransaction({"etherToSend":etherToSend, "sender":accounts[1], "operation":crowdsale.buy, "expectedResult":"success"});
      // const finalBalance = await web3.eth.getBalance(accounts[1]);
      // console.log(finalBalance);
      // const spent = initial_balance.sub(finalBalance);
      // console.log(spent);
      // const tx_receipt = await web3.eth.getTransactionReceipt(txHash);
      // console.log(tx_receipt);
      // const expected_spent = etherToSend + web3.fromWei(tx_receipt.gasUsed * GAS_PRICE);
      // console.log(expected_spent);
      // assert.isTrue(spent.equals(expected_spent));
      // const total_collected = await crowdsale.weiRaised();
      // (await web3.eth.getBalance(multiSigWallet.address)).should.be.bignumber.and.equal(total_collected);
      // investmentPerAccount[accounts[1]] = investmentPerAccount[accounts[1]].plus(etherToSend);
    } else {
      console.log("I can't understand what's happening");
    }
  });

  it_synched('Checks that customers can buy using its id', async function() {
    const etherToSend = 1;
    await mineTransaction({"etherToSend":etherToSend, "sender":accounts[2], "operation":crowdsale.buyWithCustomerId, "expectedResult":"success", "id":123});
    investmentPerAccount[accounts[2]] = investmentPerAccount[accounts[2]].plus(etherToSend);
    (await crowdsaleToken.investedAmountOf(accounts[2])).should.be.bignumber.and.equal(investmentPerAccount[accounts[2]]);
  });


  it_synched('Pauses and resumes the contribution', async function() {
    const etherToSend = 1;
    await mineTransaction({"operation":crowdsale.halt, "expectedResult":"success"});
    assert.isTrue(await crowdsale.halted());
    await mineTransaction({"etherToSend":etherToSend, "sender":accounts[2], "operation":crowdsale.buy, "expectedResult":"failure"});
    await mineTransaction({"operation":crowdsale.unhalt, "expectedResult":"success"});
    assert.isFalse(await crowdsale.halted());
    const collectedBefore = await crowdsale.weiRaised();
    await mineTransaction({"etherToSend":etherToSend, "sender":accounts[2], "operation":crowdsale.buy, "expectedResult":"success"});
    investmentPerAccount[accounts[2]] = investmentPerAccount[accounts[2]].plus(etherToSend);
    const collectedAfter = await crowdsale.weiRaised();
    assert.isTrue(web3.fromWei(collectedBefore).lessThan(web3.fromWei(collectedAfter)));
  });

  it_synched('Check transfers fail before tokens are released', async function() {
    await mineTransaction({"operation":crowdsaleToken.transfer, "sender":accounts[1], "tokensToSend":1, "receiver":accounts[2], "expectedResult":"failure"});
  });

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