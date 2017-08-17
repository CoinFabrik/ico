const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const HubiiCrowdsale = artifacts.require('./HubiiCrowdsale.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol');
const config = require('../config.js');

module.exports = function(deployer, network, accounts) {

	deployer.then(function() {
		CrowdsaleToken.at(CrowdsaleToken.address).transferOwnership(HubiiCrowdsale.address);
	});
	deployer.then(function() {
		HubiiCrowdsale.at(HubiiCrowdsale.address).finishInitialization(CrowdsaleToken.address);
	});
};