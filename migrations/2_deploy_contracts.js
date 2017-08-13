const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const HubiiCrowdsale = artifacts.require('./HubiiCrowdsale.sol');

const config = require('../config.js');

// const MW_address = "0x931F6E5c89dD5559D3820cFBd1975BA5d92F87E9";


module.exports = function(deployer, network, accounts) {
    deployer.deploy(SafeMath)
    .catch(function(error) {
        console.log(error);
    });
    deployer.link(SafeMath, HubiiCrowdsale);
    // const MW_contract = [ MultiSigWallet, [], 1 ];
    deployer.deploy(MultiSigWallet, config.multisig_owners, 1)
    .then(function() {
        deployer.deploy(HubiiCrowdsale, MultiSigWallet.address, config.startBlock, config.endBlock);})
    .catch(function(error) {
        console.log(error);
    });
};