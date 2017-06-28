const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const FlatPricing = artifacts.require('./FlatPricing.sol');
const BonusFinalizeAgent = artifacts.require('./BonusFinalizeAgent.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol');
const DynamicCeiling = artifacts.require('./DynamicCeiling.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');

const CURVES = require('../config/conf.js').CURVES;

const setHiddenCurves = require('../helpers/hiddenCurves.js').setHiddenCurves;
const assertFail = require('./helpers/assertFail');

contract('Crowdsale', function(accounts) {
    let id_time = 1;
    // Can be made async with sendAsync()
    function increaseTime(delta_seconds) {
        web3.currentProvider.send({ "jsonrpc": "2.0", method: "evm_increaseTime", "id": id_time, "params": [ delta_seconds ] });
        id_time++;
    }
    const EXAMPLE_ADDRESS_1 = accounts[1];

    const GAS = 300000;
    const GAS_PRICE = 20000000000;

    let crowdsaleToken = CrowdsaleToken.deployed().then(function(instance) {crowdsaleToken = instance});
    let flatPricing = FlatPricing.deployed().then(function(instance) {flatPricing = instance});
    let multiSigWallet = MultiSigWallet.deployed().then(function(instance) {multiSigWallet = instance});
    let dynamicCeiling = DynamicCeiling.deployed().then(function(instance) {dynamicCeiling = instance});
    let crowdsale = Crowdsale.deployed().then(function(instance) {crowdsale = instance});
    let bonusFinalizeAgent = BonusFinalizeAgent.deployed().then(function(instance) {bonusFinalizeAgent = instance});
    let init_prom = Promise.all([ crowdsaleToken, flatPricing, multiSigWallet, dynamicCeiling, crowdsale, bonusFinalizeAgent ]);

    let cur;
    let lim;
    let divs = 30;

    //TODO: add error logging?
    const it_synched = function(message, test_f) {
        it(message, function() { return init_prom.then(test_f); });
    }

    it_synched('Checks contract\'s health', async function() {
        assert(await crowdsale.isFinalizerSane() && await crowdsale.isPricingSane() && await crowdsale.isCeilingSane());
    });

    it_synched('Checks that nobody can buy before the sale starts', async function() {
        // TODO changing testrpc time
    });

    it_synched('Reveals a curve, moves time to start of the ICO, and does the first buy', async function() {
        await dynamicCeiling.revealCurve(
            CURVES[0][0],
            CURVES[0][1],
            CURVES[0][2],
            false,
            web3.sha3('pwd0'));

        // TODO: move time (right now START_DATE is a past date)

        lim = 3;
        cur = 0;

        let etherToSend = 1;

        await crowdsale.buy.sendTransaction({value: web3.toWei(etherToSend, 'ether'), gas: GAS, gasPrice: GAS_PRICE, from: EXAMPLE_ADDRESS_1});

        const b = Math.min(etherToSend, ((lim - cur) / divs));
        cur += b;

        const balance = await crowdsaleToken.balanceOf(EXAMPLE_ADDRESS_1);

        assert.equal(web3.fromWei(balance, 'ether').toNumber(), (b * (10 ** DECIMALS)) / PRICE);
    });

    it_synched('Returns the remaining of a transaction', async function() {
        const initialBalance = await web3.eth.getBalance(EXAMPLE_ADDRESS_1);
        let etherToSend = 5;
        await crowdsale.buy.sendTransaction({value: web3.toWei(etherToSend), gas: GAS, gasPrice: GAS_PRICE, from: EXAMPLE_ADDRESS_1});
        const finalBalance = await web3.eth.getBalance(EXAMPLE_ADDRESS_1);

        const b = Math.min(etherToSend, ((lim - cur) / divs));
        cur += b;

        const spent = web3.fromWei(initialBalance.sub(finalBalance)).toNumber();
        assert.isAbove(spent, b);
        // TODO: find a better approximation
        assert.isBelow(spent, b + 0.006);

        const totalCollected = await crowdsale.weiRaised();
        assert.equal(web3.fromWei(totalCollected), cur);

        const balanceContributionWallet = await web3.eth.getBalance(multiSigWallet.address);
        assert.equal(web3.fromWei(balanceContributionWallet), cur);
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