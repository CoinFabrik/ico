const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const HubiiCrowdsale = artifacts.require('./HubiiCrowdsale.sol');
const config = require('../config.js');

module.exports = function(deployer, network, accounts) {
        HubiiCrowdsale.at(HubiiCrowdsale.address).setEarlyParticipantWhitelist("0xC5BaA5Eeb01C01900d7DB0f9fF63b39985AB8390",true);
        HubiiCrowdsale.at(HubiiCrowdsale.address).setEarlyParticipantWhitelist("0x79e7Af1FD59654580d41186f7e0e72134f1eACc4",true);
        HubiiCrowdsale.at(HubiiCrowdsale.address).setEarlyParticipantWhitelist("0x81549686EF24E8bcE44A8Cf8F41C52E4a140911B",true);
        HubiiCrowdsale.at(HubiiCrowdsale.address).setEarlyParticipantWhitelist("0xBdd2D799cE3e1d0e4987448DCB1d054962a855b6",true);
        HubiiCrowdsale.at(HubiiCrowdsale.address).setEarlyParticipantWhitelist("0xa4793E13f77bf49dEA75423eCc858829D4262a4B",true);
        HubiiCrowdsale.at(HubiiCrowdsale.address).setEarlyParticipantWhitelist("0x1266Bc91e136333D977c5aC56eA9Cda1deb32C01",true);
};