const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');

// const MW_address = "0x931F6E5c89dD5559D3820cFBd1975BA5d92F87E9";


module.exports = function(deployer, network, accounts) {
  if (network == "test") return;
  const config = require('../config.js')(web3, network);
  deployer.deploy(SafeMath);
  deployer.link(SafeMath, Crowdsale);
  if (network != "liveNet") {
    deployer.deploy(MultiSigWallet, config.multisig_owners, 1, {gas: 2000000})
    .then(async function() {
      await deployer.deploy(Crowdsale, MultiSigWallet.address, config.startBlock, config.endBlock, accounts[0], {gas: 5000000});
    });
  }
  else {
    // !! In production deployment we use config.MW_address as the address of the multisig wallet
    deployer.deploy(Crowdsale, config.MW_address, config.startBlock, config.endBlock, accounts[0], {gas: 5000000});
  }
};
