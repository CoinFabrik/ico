const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const FlatPricing = artifacts.require('./FlatPricing.sol');
const BonusFinalizeAgent = artifacts.require('./BonusFinalizeAgent.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol');
const DynamicCeiling = artifacts.require('./DynamicCeiling.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');

const setHiddenCurves = require('./helpers/hiddenCurves.js').setHiddenCurves;

contract('Crowdsale', function(accounts) {
    const TOKEN_NAME = 'TokenI';
    const TOKEN_SYMBOL = 'TI';
    const INITIAL_SUPPLY = 1000;
    const DECIMALS = 2;
    const MINTABLE = true;
    const PRICE = 500;
    const START_DATE = 1478867200;
    const END_DATE = 1500000000;
    const MINIMUM_FUNDING_GOAL = 2000;
    const BONUS_BASE_POINTS = 300000; // equivalent to 30%
    const CURVES = [
        [web3.toWei(3), 30, 10**12],
        [web3.toWei(8), 30, 10**12],
        [web3.toWei(15), 30, 10**12],
    ];
    const NUM_HIDDEN_CURVES = 7;
    const EXAMPLE_ADDRESS_1 = accounts[1];

    const GAS = 300000;
    const GAS_PRICE = 20000000000;

    let crowdsaleToken;
    let flatPricing;
    let multiSigWallet;
    let dynamicCeiling;
    let crowdsale;
    let bonusFinalizeAgent;

    let cur;
    let lim;
    let divs = 30;

    it('Deploys all the contracts', async function() {
        crowdsaleToken = await CrowdsaleToken.new(TOKEN_NAME, TOKEN_SYMBOL, INITIAL_SUPPLY, DECIMALS, MINTABLE);
        flatPricing = await FlatPricing.new(PRICE);
        multiSigWallet = await MultiSigWallet.new([0x4cdabc27b48893058aa1675683af3485e4409eff], 1);
        dynamicCeiling = await DynamicCeiling.new();
        crowdsale = await Crowdsale.new(crowdsaleToken.address, flatPricing.address, dynamicCeiling.address, multiSigWallet.address, START_DATE,  END_DATE,  MINIMUM_FUNDING_GOAL);
        bonusFinalizeAgent = await BonusFinalizeAgent.new(crowdsaleToken.address, crowdsale.address, BONUS_BASE_POINTS, multiSigWallet.address);

        await setHiddenCurves(dynamicCeiling, CURVES);

        await crowdsaleToken.setMintAgent(crowdsale.address, true);
        await crowdsaleToken.setMintAgent(bonusFinalizeAgent.address, true);
        await crowdsaleToken.setReleaseAgent(bonusFinalizeAgent.address);
        await crowdsaleToken.transferOwnership(multiSigWallet.address);
    
        await crowdsale.setFinalizeAgent(bonusFinalizeAgent.address);
        await crowdsale.transferOwnership(multiSigWallet.address);
    });

    it('Checks contract\'s health', async function() {
        assert(crowdsale.isFinalizerSane() && crowdsale.isPricingSane() && crowdsale.isCeilingSane());
    });

    it('Checks that nobody can buy before the sale starts', async function() {
        // TODO changing testrpc time
    });

    it('Reveals a curve, moves time to start of the ICO, and does the first buy', async function() {
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

    it('Returns the remaining of a transaction', async function() {
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

});