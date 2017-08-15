const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const HubiiCrowdsale = artifacts.require('./HubiiCrowdsale.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol')
const config = require('../config.js');

const MW_address = "0x931F6E5c89dD5559D3820cFBd1975BA5d92F87E9";


module.exports = function(deployer, network, accounts) {
    deployer.deploy(SafeMath)
    .catch(function(error) {
        console.log(error);
    });
    deployer.link(SafeMath, HubiiCrowdsale);
    // TODO: change to use client's MultiSigWallet
    // const MW_contract = [ MultiSigWallet, [0x485de458fbcac6a7d35227842d652641384cb333], 1 ];
    const HC_contract = [ HubiiCrowdsale, config.MW_address, config.startDate, config.endDate ];
    const CT_contract = [ CrowdsaleToken, config.tokenName, config.tokenSymbol, config.initialSupply, config.decimals, config.MW_address, config.mintable ];
    deployer.deploy([ HC_contract, CT_contract ]);
    deployer.then(async function() {
        await CrowdsaleToken.at(CrowdsaleToken.address).transferOwnership(HubiiCrowdsale.address);
        await HubiiCrowdsale.at(HubiiCrowdsale.address).finishInitialization(CrowdsaleToken.address);
    });
};