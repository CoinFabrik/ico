const fs = require('fs');

const config = require('../config.js');
const assertFail = require('./helpers/assertFail.js');
var testrpc = require('./helpers/testrpc.json');

const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const FlatPricing = artifacts.require('./FlatPricing.sol');
const BonusFinalizeAgent = artifacts.require('./BonusFinalizeAgent.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');

const DECIMALS = config.DECIMALS;
const PRICE = config.PRICE;
const START_DATE = config.START_DATE;
const GAS = 300000;
const GAS_PRICE = 20000000000;

contract('Crowdsale', function(accounts) {
    const EXAMPLE_ADDRESS_0 = accounts[0];
    const EXAMPLE_ADDRESS_1 = accounts[1];

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

    // Current amount of ether raised
    let cur = 0;

    let id_time = 1;
    // TODO: check whether we can go back in time
    // Can be made async with sendAsync()
    function increaseTime(delta_seconds) {
        web3.currentProvider.send({ "jsonrpc": "2.0", method: "evm_increaseTime", "id": id_time, "params": [ delta_seconds ] });
        id_time++;

        testrpc.timeChanged = testrpc.timeChanged + delta_seconds;
        fs.writeFileSync('./test/helpers/testrpc.json', JSON.stringify(testrpc, null, 2));
        testrpc = require('./helpers/testrpc.json');
    }

    // TODO: add error logging?
    const it_synched = function(message, test_f) {
        it(message, function() {
            return init_prom
            .then(test_f);
        });
    }

    it_synched('Checks contract\'s health', async function() {
        assert(await crowdsale.isFinalizerSane() && await crowdsale.isPricingSane());
    });

    it_synched('Moves time to a day before the ICO and checks that nobody can buy', async function() {
        let actualTime = (Date.now() / 1000) | 0;
        var timeDelta = actualTime - START_DATE + (60 * 60 * 24) + testrpc.timeChanged;
        timeDelta = timeDelta * (-1);
        increaseTime(timeDelta);
        await assertFail(async function() {
            await crowdsale.buy.sendTransaction({value: web3.toWei(1), gas: GAS, gasPrice: GAS_PRICE, from: EXAMPLE_ADDRESS_1});
        });
    });

    it_synched('Moves time to start of the ICO, buys, and checks that tokens belong to new owner', async function() {
        // We move time forward if it's necessary
        var timeDelta = START_DATE - (((Date.now() / 1000) | 0) + testrpc.timeChanged); //!! cast expression to int with OR 0
        increaseTime(timeDelta);

        let etherToSend = 1;

        await crowdsale.buy.sendTransaction({value: web3.toWei(etherToSend, 'ether'), gas: GAS, gasPrice: GAS_PRICE, from: EXAMPLE_ADDRESS_1});
        const balance = await crowdsaleToken.balanceOf(EXAMPLE_ADDRESS_1);

        assert.equal(web3.fromWei(balance, 'ether').toNumber(), (etherToSend * (10 ** DECIMALS)) / PRICE);
        
        cur += etherToSend;
    });

    it_synched('Checks that ether goes where it should after a purchase', async function() {
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