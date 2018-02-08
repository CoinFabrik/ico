// const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');


module.exports = function(deployer, network, accounts) {
  // const config = require('../config.js')(web3, network);
  deployer.then(function() {
    const crowdsale = Crowdsale.at(Crowdsale.address);
    
    crowdsale.setEarlyParticipantWhitelist("0x9ddc080f31778dc5c2be20a51483fccd3ce17afd", true);
    crowdsale.setEarlyParticipantWhitelist("0x25F474bF97eBaFB6D4AC26F2DC897e35cdD088Af", true);

    // Testing addresses
    // crowdsale.setEarlyParticipantWhitelist("0x72FC254FCE8DD4B0E92A90035AFE90A218E0F206", true);
    crowdsale.setEarlyParticipantWhitelist("0x8ffC991Fc4C4fC53329Ad296C1aFe41470cFFbb3", true);
  }); 
};