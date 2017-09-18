const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');
const config = require('../config.js');

module.exports = function(deployer, network, accounts) {
        deployer.then(function() {
            const crowdsale = Crowdsale.at(Crowdsale.address);
        }); 
};