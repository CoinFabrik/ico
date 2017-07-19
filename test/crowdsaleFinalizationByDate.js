const config = require('../config.js');
const assertFail = require('./helpers/assertFail');

const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const FlatPricing = artifacts.require('./FlatPricing.sol');
const BonusFinalizeAgent = artifacts.require('./BonusFinalizeAgent.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol');
const FixedCeiling = artifacts.require('./FixedCeiling.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');

//Test para finalizacion por fecha
contract('Crowdsale', function(accounts) {
    let id_time = 1;
    var increased_time = 0;
    // TODO: check whether we can go back in time
    // Can be made async with sendAsync()
    // These tests are written assuming a fresh instance of testrpc
    // Though, as a reminder, the result of the evm_increaseTime has the total increased time of the instance
    function increaseTime(delta_seconds) {
        web3.currentProvider.send({ "jsonrpc": "2.0", method: "evm_increaseTime", "id": id_time, "params": [ delta_seconds ] });
        id_time++;
        increased_time += delta_seconds;
    }

    function currentTime() {
        return ((Date.now() / 1000) | 0) + increased_time;
    }

    const GAS = 300000;
    const GAS_PRICE = 20000000000;

    const exampleAddress0 = accounts[0];
    const exampleAddress1 = accounts[1];

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
    // Current amount of ether purchased by exampleAddress1
    let cur = 0;

    // Error logging handled by mocha/chai
    const it_synched = function(message, test_f) {
        it(message, function() {
            return promise_chain
            .then(test_f);
        });
    }

    it_synched('Checks contract\'s health', async function() {
        assert(await crowdsale.isFinalizerSane() && await crowdsale.isPricingSane() && await crowdsale.isCeilingSane());
    });

    it_synched('Checks that nobody can buy before the sale starts', async function() {
        let actualTime = currentTime();
        if (actualTime < config.startDate) {
            await assertFail(async function() {
                await crowdsale.buy.sendTransaction({value: web3.toWei(1), gas: GAS, gasPrice: GAS_PRICE, from: exampleAddress1});
            });
        }
    });

    it_synched('Moves time to start of the ICO, buys, and checks that tokens belong to new owner', async function() {
        // We move time forward if it's necessary
        const timeDelta = config.startDate - currentTime(); //!! cast expression to int with OR 0
        if (timeDelta > 0)
            increaseTime(timeDelta + 1);
    
        let etherToSend = 1;

        await crowdsale.buy.sendTransaction({value: web3.toWei(etherToSend), gas: GAS, gasPrice: GAS_PRICE, from: exampleAddress1});
        const balance = await crowdsaleToken.balanceOf(exampleAddress1);

        assert.equal(web3.fromWei(balance).toNumber(), (etherToSend * (10 ** config.decimals)) / web3.toWei(config.price));
        
        let investorCount = await crowdsale.investorCount();
        investorCount = investorCount.toNumber();
        assert.equal(investorCount, 1);

        cur += etherToSend;
    });

    it_synched('Checks that ether goes where it should after a purchase', async function() {
        const initialBalance = await web3.eth.getBalance(exampleAddress1);
        let etherToSend = 5;
        const tx = await crowdsale.buy.sendTransaction({value: web3.toWei(etherToSend), gas: GAS, gasPrice: GAS_PRICE, from: exampleAddress1});
        const finalBalance = await web3.eth.getBalance(exampleAddress1);

        const spent = web3.fromWei(initialBalance.sub(finalBalance)).toNumber();
        let tx_receipt = await web3.eth.getTransactionReceipt(tx);
        const expected_gas_usage = etherToSend + parseFloat(web3.fromWei(tx_receipt.cumulativeGasUsed * GAS_PRICE));
        assert.equal(spent, expected_gas_usage);

        const totalCollected = await crowdsale.weiRaised();
        assert.equal(web3.fromWei(totalCollected).toNumber(), cur + etherToSend);

        const balanceContributionWallet = await web3.eth.getBalance(multiSigWallet.address);
        assert.equal(web3.fromWei(balanceContributionWallet).toNumber(), cur + etherToSend);
        
        cur += etherToSend;
    });

    it_synched('Checks that customers can buy using its id', async function() {
        let etherToSend = 2;
        let id = 123;
        await crowdsale.buyWithCustomerId.sendTransaction(id, {value: web3.toWei(etherToSend), gas: GAS, gasPrice: GAS_PRICE, from: exampleAddress1});
        const balance = await crowdsaleToken.balanceOf(exampleAddress1);

        assert.equal(web3.fromWei(balance).toNumber(), ((etherToSend + cur) * (10 ** config.decimals)) / web3.toWei(config.price));

        cur += etherToSend;
    });

    it_synched('Pauses and resumes the contribution', async function() {
        await crowdsale.halt();
        await assertFail(async function() {
            await crowdsale.buy.sendTransaction({value: web3.toWei(1), gas: GAS, gasPrice: GAS_PRICE, from: exampleAddress1});
        });
        await crowdsale.unhalt();

        const collectedBefore = await crowdsale.weiRaised();
        await crowdsale.buy.sendTransaction({value: web3.toWei(1), gas: GAS, gasPrice: GAS_PRICE, from: exampleAddress1});
        const collectedAfter = await crowdsale.weiRaised();
        assert.isBelow(collectedBefore, collectedAfter);
    });

    it_synched('Check transfers fail before tokens are released', async function() {
        await assertFail(async function() {
            await crowdsaleToken.transfer(exampleAddress0, 1);
        });
    });

    it_synched('Sets funding cap', async function() {
        let initialFundingCap = await crowdsale.weiFundingCap();
        assert.equal(initialFundingCap, 0);

        let weiRaised = await crowdsale.weiRaised();
        weiRaised = weiRaised.toNumber();
        let chunkedWeiMultiple = parseInt(web3.toWei(config.chunkedMultipleCap));
        let newFundingCap = (Math.trunc(weiRaised / chunkedWeiMultiple) + 1) * chunkedWeiMultiple;
        await crowdsale.setFundingCap(newFundingCap);

        let finalFundingCap = await crowdsale.weiFundingCap();
        assert.equal(finalFundingCap.toNumber(), newFundingCap);
    });

    it_synched('Checks crowdsale finalization on success and end date reached', async function() {
        let minimumReached = await crowdsale.isMinimumGoalReached();
        assert.isFalse(minimumReached);

        let minimumFundingGoal = await crowdsale.minimumFundingGoal();
        minimumFundingGoal= minimumFundingGoal.toNumber();
        let initialWeiRaised = await crowdsale.weiRaised();
        initialWeiRaised = initialWeiRaised.toNumber();
        let remainingUntilMinimum = minimumFundingGoal - initialWeiRaised + 1;
        
        await crowdsale.buy.sendTransaction({value: remainingUntilMinimum, gas: GAS, gasPrice: GAS_PRICE, from: exampleAddress1});
        cur += remainingUntilMinimum;

        assert.isTrue(await crowdsale.isMinimumGoalReached());

        let minimumFundingWeiRaised = await crowdsale.weiRaised();

        assert.equal(minimumFundingWeiRaised.toNumber(), initialWeiRaised + remainingUntilMinimum);

        assert.isFalse(await crowdsaleToken.released());

        let timeDelta = config.endDate - currentTime(); //!! cast expression to int with OR 0
        if (timeDelta > 0)
            increaseTime(timeDelta + 1);

        await crowdsale.finalize();

        const tokensSold = await crowdsale.tokensSold();
        const teamFinalBalance = await crowdsaleToken.balanceOf(multiSigWallet.address);
        assert.equal(teamFinalBalance.toNumber(), Math.floor(tokensSold.toNumber() * config.bonusBasePoints / 10000)); //Solidity truncates non-literal divisions.

        let finalized = await crowdsale.finalized();
        assert.isTrue(finalized)
        assert.isTrue(await crowdsaleToken.released());

        let initialBalance0 = await crowdsaleToken.balanceOf(exampleAddress0);
        assert.equal(initialBalance0, 0);

        const weiToSend = 1;
        await crowdsaleToken.transfer.sendTransaction(exampleAddress0, weiToSend, {from: exampleAddress1});

        let finalBalance0 = await crowdsaleToken.balanceOf(exampleAddress0);
        assert.equal(finalBalance0, weiToSend);
        web3.currentProvider.send({ "jsonrpc": "2.0", method: "evm_revert", "id": id_time, "params": [ 1 ] });
    });
});