const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');

const config = require('../config.js')(web3);

// const MW_address = "0x931F6E5c89dD5559D3820cFBd1975BA5d92F87E9";


module.exports = function(deployer, network, accounts) {
    deployer.deploy(SafeMath);
    deployer.link(SafeMath, Crowdsale);
    if (network != "liveNet") {
        deployer.deploy(MultiSigWallet, config.tests.multisig_owners, 1, {gas: 2000000})
        .then(function() {
            deployer.deploy(Crowdsale, MultiSigWallet.address, config.tests.startBlock, config.tests.endBlock, {gas: 4000000});
        });
    }
    else {
        // !! In production deployment we use config.MW_address as the address of the multisig wallet
        deployer.deploy(Crowdsale, config.MW_address, config.startBlock, config.endBlock, {gas: 4000000});
    }
};