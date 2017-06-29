const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const FlatPricing = artifacts.require('./FlatPricing.sol');
const BonusFinalizeAgent = artifacts.require('./BonusFinalizeAgent.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol');
const FixedCeiling = artifacts.require('./FixedCeiling.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');

const config = require('../config.js');

const TOKEN_NAME = config.TOKEN_NAME;
const TOKEN_SYMBOL = config.TOKEN_SYMBOL;
const INITIAL_SUPPLY = config.INITIAL_SUPPLY;
const DECIMALS = config.DECIMALS;
const MINTABLE = config.MINTABLE;
const PRICE = config.PRICE;
const START_DATE = config.START_DATE;
const END_DATE = config.END_DATE;
const MINIMUM_FUNDING_GOAL = config.MINIMUM_FUNDING_GOAL;
const BONUS_BASE_POINTS = config.BONUS_BASE_POINTS;

module.exports = function(deployer) {
    deployer.deploy(SafeMath);
    deployer.link(SafeMath, FlatPricing);
    deployer.link(SafeMath, BonusFinalizeAgent);
    deployer.link(SafeMath, CrowdsaleToken);
    deployer.link(SafeMath, FixedCeiling);
    deployer.link(SafeMath, Crowdsale);

    let CT_contract = [ CrowdsaleToken, TOKEN_NAME, TOKEN_SYMBOL, INITIAL_SUPPLY, DECIMALS, MINTABLE ];
    let FP_contract = [ FlatPricing, PRICE ];
    let FC_contract = [ FixedCeiling, web3.toWei(config.CHUNKED_MULTIPLE_CAP), web3.toWei(config.LIMIT_PER_ADDRESS) ];
    // TODO: change to use client's MultiSigWallet
    let MW_contract = [ MultiSigWallet, [0x4cdabc27b48893058aa1675683af3485e4409eff], 1 ];
    
    return deployer.deploy([ CT_contract, FP_contract, FC_contract, MW_contract ])
    .then(async function() {
        await deployer.deploy(Crowdsale, CrowdsaleToken.address, FlatPricing.address, FixedCeiling.address, MultiSigWallet.address, START_DATE,  END_DATE,  MINIMUM_FUNDING_GOAL);
    })
    .then(async function() {
        await deployer.deploy(BonusFinalizeAgent, CrowdsaleToken.address, Crowdsale.address, BONUS_BASE_POINTS, MultiSigWallet.address);
    })
    .then(async function() {
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

        await Promise.all([ CT_prom, C_prom ]);
    })
    .catch(function(error) {
        console.log(error);
    });
};