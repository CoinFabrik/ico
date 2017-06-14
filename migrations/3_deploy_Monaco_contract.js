var SafeMathLib = artifacts.require("./TokenMarket/SafeMathLib.sol");
var CrowdsaleToken = artifacts.require("./TokenMarket/CrowdsaleToken.sol");
var EthTranchePricing = artifacts.require("./TokenMarket/EthTranchePricing.sol");
var MultiSigWallet = artifacts.require("./TokenMarket/MultiSigWallet.sol");
var MintedEthCappedCrowdsale = artifacts.require("./TokenMarket/MintedEthCappedCrowdsale.sol");

module.exports = function(deployer) {
    deployer.deploy(SafeMathLib);
    deployer.link(SafeMathLib, MintedEthCappedCrowdsale);

    deployer.deploy(CrowdsaleToken, "TokenI", "TI", 1000, 2, true);
    deployer.deploy(EthTranchePricing);
    deployer.deploy(MultiSigWallet);
    deployer.deploy(MintedEthCappedCrowdsale,
        CrowdsaleToken.address, // _token 
        EthTranchePricing.address, // _pricingStrategy
        MultiSigWallet.address, // _multisigWallet 
        1498867200, // _start (the UNIX timestamp start date of the crowdsale)
        1500000000, // _end
        1000, // _minimumFundingGoal
        1000000000 // _weiCap (maximum amount of wei this crowdsale can raise)
        );

};