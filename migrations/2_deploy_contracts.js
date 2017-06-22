const RandomBytes = require('random-bytes');

const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const FlatPricing = artifacts.require('./FlatPricing.sol');
const BonusFinalizeAgent = artifacts.require('./BonusFinalizeAgent.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol');
const DynamicCeiling = artifacts.require('./DynamicCeiling.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');

// TODO: adapt to client needs
const TOKEN_NAME = 'TokenI';
const TOKEN_SYMBOL = 'TI';
const INITIAL_SUPPLY = 1000;
const DECIMALS = 2;
const MINTABLE = true;
const PRICE = 500;
const START_DATE = 1498867200;
const END_DATE = 1500000000;
const MINIMUM_FUNDING_GOAL = 2000;
const BONUS_BASE_POINTS = 300000; // equivalent to 30%
const CURVES = [
    [web3.toWei(1000), 30, 10**12],
    [web3.toWei(21000), 30, 10**12],
    [web3.toWei(61000), 30, 10**12],
];
const NHIDDENCURVES = 7;

const setHiddenCurves = async function(dynamicCeiling, curves, nHiddenCurves) {
    let hashes = [];
    let i = 0;
    for (let c of curves) {
        let salt = await RandomBytes(32);
        console.log('Curve', i, 'has salt:', salt.toString('hex'));
        let h = await dynamicCeiling.calculateHash(c[0], c[1], c[2], i === curves.length - 1, salt);
        hashes.push(h);
        i += 1;
    }
    for (; i < nHiddenCurves; i += 1) {
        let salt = RandomBytes(32);
        hashes.push(web3.sha3(salt));
    }
    await dynamicCeiling.setHiddenCurves(hashes);
    console.log(i, 'curves set');
};

module.exports = async function(deployer) {
    deployer.deploy(SafeMath);
    deployer.link(SafeMath, FlatPricing);
    deployer.link(SafeMath, BonusFinalizeAgent);
    deployer.link(SafeMath, CrowdsaleToken);
    deployer.link(SafeMath, DynamicCeiling);
    deployer.link(SafeMath, Crowdsale);

    try {
        await deployer.deploy(CrowdsaleToken, TOKEN_NAME, TOKEN_SYMBOL, INITIAL_SUPPLY, DECIMALS, MINTABLE);
        console.log('CrowdsaleToken:', CrowdsaleToken.address);
        
        await deployer.deploy(FlatPricing, PRICE);
        console.log('FlatPricing:', FlatPricing.address);
        
        // TODO: change to use client's MultiSigWallet
        await deployer.deploy(MultiSigWallet, [0x4cdabc27b48893058aa1675683af3485e4409eff], 1);
        console.log('MultiSigWallet:', MultiSigWallet.address);
        
        // TODO: set proper owner on DynamicCeiling
        await deployer.deploy(DynamicCeiling, 0x4cdabc27b48893058aa1675683af3485e4409eff);
        console.log('DynamicCeiling:', DynamicCeiling.address);
        
        await deployer.deploy(Crowdsale, CrowdsaleToken.address, DynamicCeiling.address, FlatPricing.address, MultiSigWallet.address, START_DATE,  END_DATE,  MINIMUM_FUNDING_GOAL);
        console.log('Crowdsale:', Crowdsale.address);
        
        await deployer.deploy(BonusFinalizeAgent, CrowdsaleToken.address, Crowdsale.address, BONUS_BASE_POINTS, MultiSigWallet.address);
        console.log('BonusFinalizeAgent:', BonusFinalizeAgent.address);

        DynamicCeiling.deployed()
        .then(function(ceilingInstance) {
            setHiddenCurves(ceilingInstance, CURVES, NHIDDENCURVES);
        });

        CrowdsaleToken.deployed()
        .then(async function(tokenInstance) {
            await tokenInstance.setMintAgent(Crowdsale.address, true);
            await tokenInstance.setMintAgent(BonusFinalizeAgent.address, true);
            await tokenInstance.setReleaseAgent(BonusFinalizeAgent.address);
            tokenInstance.transferOwnership(MultiSigWallet.address);
        });

        Crowdsale.deployed()
        .then(async function(crowdsaleInstance) {
            await crowdsaleInstance.setFinalizeAgent(BonusFinalizeAgent.address);
            crowdsaleInstance.transferOwnership(MultiSigWallet.address);
        });

    }
    catch(error) {
        console.log(error);
    }

};