const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const FlatPricing = artifacts.require('./FlatPricing.sol');
const BonusFinalizeAgent = artifacts.require('./BonusFinalizeAgent.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');

const config = require('../config/conf.js');
const assertFail = require('./helpers/assertFail');
const DECIMALS = config.DECIMALS;
const PRICE = config.PRICE;

contract('Crowdsale', function(accounts) {
    let id_time = 1;
    // Can be made async with sendAsync()
    function increaseTime(delta_seconds) {
        web3.currentProvider.send({ "jsonrpc": "2.0", method: "evm_increaseTime", "id": id_time, "params": [ delta_seconds ] });
        id_time++;
    }
    const EXAMPLE_ADDRESS_0 = accounts[0];
    const EXAMPLE_ADDRESS_1 = accounts[1];

    const GAS = 300000;
    const GAS_PRICE = 20000000000;

    let crowdsaleToken;
    let flatPricing;
    let multiSigWallet;
    let crowdsale;
    let bonusFinalizeAgent;
    let init_prom = Promise.all([ CrowdsaleToken.deployed().then(function(instance) {crowdsaleToken = instance}),
                                  FlatPricing.deployed().then(function(instance) {flatPricing = instance}),
                                  MultiSigWallet.deployed().then(function(instance) {multiSigWallet = instance}),
                                  Crowdsale.deployed().then(function(instance) {crowdsale = instance}),
                                  BonusFinalizeAgent.deployed().then(function(instance) {bonusFinalizeAgent = instance}) 
                                ]);

    // current balance of EXAMPLE_ADDRESS_1
    let cur = 0;

    //TODO: add error logging?
    const it_synched = function(message, test_f) {
        it(message, function() { return init_prom.then(test_f); });
    }

    it_synched('Checks contract\'s health', async function() {
        assert(await crowdsale.isFinalizerSane() && await crowdsale.isPricingSane());
    });

    it_synched('Checks that nobody can buy before the sale starts', async function() {
        // TODO changing testrpc time
    });

    it_synched('Moves time to start of the ICO, and does the first buy', async function() {

        // We move time forward if it's necessary
        // TODO: check whether we can go back in time
        time_delta = config.START_DATE - ((Date.now() / 1000) | 0); //!! cast expression to int with OR 0
        if (time_delta > 0)
            increaseTime(time_delta);

        let etherToSend = 1;

        await crowdsale.buy.sendTransaction({value: web3.toWei(etherToSend, 'ether'), gas: GAS, gasPrice: GAS_PRICE, from: EXAMPLE_ADDRESS_1});

        const balance = await crowdsaleToken.balanceOf(EXAMPLE_ADDRESS_1);

        assert.equal(web3.fromWei(balance, 'ether').toNumber(), (etherToSend * (10 ** DECIMALS)) / PRICE);
        cur += etherToSend;
    });

    it_synched('Returns the remainder of a transaction', async function() {
        const initialBalance = await web3.eth.getBalance(EXAMPLE_ADDRESS_1);
        let etherToSend = 5;
        await crowdsale.buy.sendTransaction({value: web3.toWei(etherToSend), gas: GAS, gasPrice: GAS_PRICE, from: EXAMPLE_ADDRESS_1});
        const finalBalance = await web3.eth.getBalance(EXAMPLE_ADDRESS_1);


        const spent = web3.fromWei(initialBalance.sub(finalBalance)).toNumber();
        assert.isAbove(spent, etherToSend);
        // TODO: find a better approximation
        assert.isBelow(spent, etherToSend + 0.006);

        const totalCollected = await crowdsale.weiRaised();
        assert.equal(web3.fromWei(totalCollected).toNumber(), cur + etherToSend);

        const balanceContributionWallet = await web3.eth.getBalance(multiSigWallet.address);
        assert.equal(web3.fromWei(balanceContributionWallet).toNumber(), cur + etherToSend);
        cur += etherToSend;
    });

    it_synched('Pauses and resumes the contribution', async function() {
        await crowdsale.halt();
        await assertFail(async function() {
            await crowdsale.buy.sendTransaction({value: web3.toWei(1), gas: GAS, gasPrice: GAS_PRICE, from: EXAMPLE_ADDRESS_1});
        });
        await crowdsale.unhalt();

        const collectedBefore = await crowdsale.weiRaised();
        await crowdsale.buy.sendTransaction({value: web3.toWei(1), gas: GAS, gasPrice: GAS_PRICE, from: EXAMPLE_ADDRESS_1});
        const collectedAfter = await crowdsale.weiRaised();
        assert.isBelow(collectedBefore, collectedAfter);
    });

});