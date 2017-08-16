const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol');
const config = require('../config.js');

module.exports = function(deployer, network, accounts) {

    // TODO: change to use client's MultiSigWallet
    // const MW_contract = [ MultiSigWallet, [0x485de458fbcac6a7d35227842d652641384cb333], 1 ];
    const CT_contract = [ CrowdsaleToken, config.tokenName, config.tokenSymbol, config.initialSupply, config.decimals, config.MW_address, config.mintable ];
    deployer.deploy([ CT_contract ]);
};