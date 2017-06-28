const RandomBytes = require('random-bytes');

const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const FlatPricing = artifacts.require('./FlatPricing.sol');
const BonusFinalizeAgent = artifacts.require('./BonusFinalizeAgent.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol');
const DynamicCeiling = artifacts.require('./DynamicCeiling.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');

// TODO: adapt to client needs
const Config = require('../config/conf.js');

const TOKEN_NAME = Config.TOKEN_NAME;
const TOKEN_SYMBOL = Config.TOKEN_SYMBOL;
const INITIAL_SUPPLY = Config.INITIAL_SUPPLY;
const DECIMALS = Config.DECIMALS;
const MINTABLE = Config.MINTABLE;
const PRICE = Config.PRICE;
const START_DATE = Config.START_DATE;
const END_DATE = Config.END_DATE;
const MINIMUM_FUNDING_GOAL = Config.MINIMUM_FUNDING_GOAL;
const BONUS_BASE_POINTS = Config.BONUS_BASE_POINTS;
const CURVES = Config.CURVES;
const NUM_HIDDEN_CURVES = Config.NUM_HIDDEN_CURVES;

const setHiddenCurves = require('../helpers/hiddenCurves.js').setHiddenCurves;

module.exports = function(deployer) {
    deployer.deploy(SafeMath);
    deployer.link(SafeMath, FlatPricing);
    deployer.link(SafeMath, BonusFinalizeAgent);
    deployer.link(SafeMath, CrowdsaleToken);
    deployer.link(SafeMath, DynamicCeiling);
    deployer.link(SafeMath, Crowdsale);

    let CT_contract = [ CrowdsaleToken, TOKEN_NAME, TOKEN_SYMBOL, INITIAL_SUPPLY, DECIMALS, MINTABLE ];
    let FP_contract = [ FlatPricing, PRICE ];
    let DC_contract = [ DynamicCeiling ];
    let MW_contract = [ MultiSigWallet, [0x4cdabc27b48893058aa1675683af3485e4409eff], 1 ];
    
    return deployer.deploy([ CT_contract, FP_contract, DC_contract, MW_contract ])
    .then(async function() {
        await deployer.deploy(Crowdsale, CrowdsaleToken.address, FlatPricing.address, DynamicCeiling.address, MultiSigWallet.address, START_DATE,  END_DATE,  MINIMUM_FUNDING_GOAL);
    })
    .then(async function() {
        await deployer.deploy(BonusFinalizeAgent, CrowdsaleToken.address, Crowdsale.address, BONUS_BASE_POINTS, MultiSigWallet.address);
    })
    .then(async function() {
        let DC_prom = DynamicCeiling.deployed()
        .then(async function(ceilingInstance) {
            console.log('Setting hidden curves in ceiling strategy\'s contract...');
            await setHiddenCurves(ceilingInstance, CURVES, NUM_HIDDEN_CURVES);
        });

        let CT_prom = CrowdsaleToken.deployed()
        .then(async function(tokenInstance) {
            console.log('Setting Crowdsale as mint agent of CrowdsaleToken...');
            await tokenInstance.setMintAgent(Crowdsale.address, true);
            console.log('Setting BonusFinalizeAgent as mint agent of CrowdsaleToken...');
            await tokenInstance.setMintAgent(BonusFinalizeAgent.address, true);
            console.log('Setting BonusFinalizeAgent as release agent of CrowdsaleToken...');
            await tokenInstance.setReleaseAgent(BonusFinalizeAgent.address);
            // console.log('Transfering ownership of CrowdsaleToken to MultiSigWallet...');
            // tokenInstance.transferOwnership(MultiSigWallet.address);
        });
        
        let C_prom = Crowdsale.deployed()
        .then(async function(crowdsaleInstance) {
            console.log('Setting BonusFinalizeAgent as finalize agent of Crowdsale...');
            await crowdsaleInstance.setFinalizeAgent(BonusFinalizeAgent.address);
            // console.log('Transfering ownership of Crowdsale contract to MultiSigWallet...');
            // crowdsaleInstance.transferOwnership(MultiSigWallet.address);
        });

        await Promise.all([ DC_prom, CT_prom, C_prom ]);
    })
    .catch(function(error) {
        console.log(error);
    });
};