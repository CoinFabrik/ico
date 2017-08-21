const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const HubiiCrowdsale = artifacts.require('./HubiiCrowdsale.sol');
const config = require('../config.js');

module.exports = function(deployer, network, accounts) {
        deployer.then(function(){
            crowdsale = HubiiCrowdsale.at(HubiiCrowdsale.address);
            crowdsale.setEarlyParticipantWhitelist("0XC5BAA5EEB01C01900D7DB0F9FF63B39985AB8390", true);
            crowdsale.setEarlyParticipantWhitelist("0X79E7AF1FD59654580D41186F7E0E72134F1EACC4", true);
            crowdsale.setEarlyParticipantWhitelist("0X81549686EF24E8BCE44A8CF8F41C52E4A140911B", true);
            crowdsale.setEarlyParticipantWhitelist("0XBDD2D799CE3E1D0E4987448DCB1D054962A855B6", true);
            crowdsale.setEarlyParticipantWhitelist("0XA4793E13F77BF49DEA75423ECC858829D4262A4B", true);
            crowdsale.setEarlyParticipantWhitelist("0X1266BC91E136333D977C5AC56EA9CDA1DEB32C01", true);
            crowdsale.setEarlyParticipantWhitelist("0XFDECC1FA040A320D9DC855667118B881B0749334", true);
            // Testing address
            // crowdsale.setEarlyParticipantWhitelist("0X72FC254FCE8DD4B0E92A90035AFE90A218E0F206", true);
            crowdsale.setFundingCap(config.fundingCap, {gas:1000000});
        }); 
};