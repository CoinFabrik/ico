const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const HubiiCrowdsale = artifacts.require('./HubiiCrowdsale.sol');

const config = require('../config.js');

// const MW_address = "0x931F6E5c89dD5559D3820cFBd1975BA5d92F87E9";


module.exports = function(deployer, network, accounts) {
    const startBlock = network == "privateTestnet" ? config.tests.startBlock : config.startBlock;
    const endBlock = network == "privateTestnet" ? config.tests.endBlock : config.endBlock;
    deployer.deploy(SafeMath, {gas: 500000});
    deployer.link(SafeMath, HubiiCrowdsale);
    if (network != "liveNet") {
        deployer.deploy(MultiSigWallet, config.multisig_owners, 1)
        .then(function() {
            deployer.deploy(HubiiCrowdsale, MultiSigWallet.address, startBlock, endBlock);
        });
    }
    else {
        // !! In production deployment change multisig address to config.MW_address
        deployer.deploy(HubiiCrowdsale, config.tests.MW_address, startBlock, endBlock);
    }
};