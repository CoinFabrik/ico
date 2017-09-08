const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const HubiiCrowdsale = artifacts.require('./Crowdsale.sol');

const config = require('../config.js');

// const MW_address = "0x931F6E5c89dD5559D3820cFBd1975BA5d92F87E9";


module.exports = function(deployer, network, accounts) {
    const startBlock = network == "privateTestnet" ? config.tests.startBlock : config.startBlock;
    const endBlock = network == "privateTestnet" ? config.tests.endBlock : config.endBlock;
    deployer.deploy(SafeMath);
    deployer.link(SafeMath, Crowdsale);
    if (network != "liveNet") {
        deployer.deploy(MultiSigWallet, config.multisig_owners, 1, {gas: 2000000})
        .then(function() {
            deployer.deploy(Crowdsale, MultiSigWallet.address, startBlock, endBlock, {gas: 5400000});
        });
    }
    else {
        // !! In production deployment we use config.MW_address as the address of the multisig wallet
        deployer.deploy(Crowdsale, config.MW_address, startBlock, endBlock, {gas: 5400000});
    }
};