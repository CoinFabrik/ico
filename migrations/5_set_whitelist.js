// const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');


module.exports = function(deployer, network, accounts) {
  if (network == "test") return;
  // const config = require('../config.js')(web3, network);
  deployer.then(function() {
    const crowdsale = Crowdsale.at(Crowdsale.address);

    // Testing addresses
    // crowdsale.setEarlyParticipantWhitelist("0x72FC254FCE8DD4B0E92A90035AFE90A218E0F206", true);
    crowdsale.setEarlyParticipantWhitelist("0x8ffC991Fc4C4fC53329Ad296C1aFe41470cFFbb3", true);
  }); 
};
