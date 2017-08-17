    const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const HubiiCrowdsale = artifacts.require('./HubiiCrowdsale.sol');
const config = require('../config.js');

module.exports = function(deployer, network, accounts) {
    deployer.deploy(SafeMath)
    .catch(function(error) {
        console.log(error);
    });
    
    deployer.link(SafeMath, HubiiCrowdsale);

    const HC_contract = [ HubiiCrowdsale, config.MW_address, config.startBlock, config.endBlock ];         
    
    deployer.deploy([HC_contract])
    .catch(function(error){
        console.log(error);
    });               
 
    // TODO: change to use client's MultiSigWallet
};