const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const FlatPricing = artifacts.require('./FlatPricing.sol');
const BonusFinalizeAgent = artifacts.require('./BonusFinalizeAgent.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol');
const FixedCeiling = artifacts.require('./FixedCeiling.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');

const config = require('../config.js');

module.exports = function(deployer, network, accounts) {
    deployer.deploy(SafeMath);
    deployer.link(SafeMath, [FlatPricing, BonusFinalizeAgent, CrowdsaleToken, FixedCeiling, Crowdsale]);

    const CT_contract = [ CrowdsaleToken, config.tokenName, config.tokenSymbol, web3.toWei(config.initialSupply), config.decimals, config.mintable ];
    // const CT_data = CrowdsaleToken.new.getData(CT_contract.slice(1, CT_contract.length));
    const FP_contract = [ FlatPricing, web3.toWei(config.price) ];
    const FC_contract = [ FixedCeiling, web3.toWei(config.chunkedMultipleCap), web3.toWei(config.limitPerAddress) ];
    // TODO: change to use client's MultiSigWallet
    // const MW_contract = [ MultiSigWallet, [0x485de458fbcac6a7d35227842d652641384cb333], 1 ];
    const MW_address = "0x931F6E5c89dD5559D3820cFBd1975BA5d92F87E9";
    const BFA_contract = [ BonusFinalizeAgent, config.bonusBasePoints, MW_address ];
    deployer.deploy([ CT_contract, FP_contract, FC_contract, BFA_contract ])
    .then(async function() {
        console.log('Setting BonusFinalizeAgent as mint agent of CrowdsaleToken...');
        await tokenInstance.setMintAgent(BonusFinalizeAgent.address, true);
        console.log('Setting BonusFinalizeAgent as release agent of CrowdsaleToken...');
        await tokenInstance.setReleaseAgent(BonusFinalizeAgent.address);
        await deployer.deploy(Crowdsale, CrowdsaleToken.address, FlatPricing.address, FixedCeiling.address, MW_address, config.startDate,  config.endDate,  web3.toWei(config.minimumFundingGoal));
    })
    .then(async function() {
        await deployer.deploy(BonusFinalizeAgent, CrowdsaleToken.address, Crowdsale.address, config.bonusBasePoints, MW_address);
    })
    .then(async function() {
        let CT_prom = CrowdsaleToken.deployed()
        .then(async function(tokenInstance) {
            console.log('Setting Crowdsale as mint agent of CrowdsaleToken...');
            await tokenInstance.setMintAgent(Crowdsale.address, true);
            // console.log('Transfering ownership of CrowdsaleToken to MultiSigWallet...');
            // tokenInstance.transferOwnership(MW_address);
        });
        
        let C_prom = Crowdsale.deployed()
        .then(async function(crowdsaleInstance) {
            console.log('Setting BonusFinalizeAgent as finalize agent of Crowdsale...');
            await crowdsaleInstance.setFinalizeAgent(BonusFinalizeAgent.address);
            // console.log('Transfering ownership of Crowdsale contract to MultiSigWallet...');
            // crowdsaleInstance.transferOwnership(MW_address);
        });

        await Promise.all([ CT_prom, C_prom ]);
    })
    .catch(function(error) {
        console.log(error);
    });
};