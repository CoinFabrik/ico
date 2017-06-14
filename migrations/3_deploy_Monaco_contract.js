var SafeMathLib = artifacts.require("./TokenMarket/SafeMathLib.sol");
var CrowdsaleToken = artifacts.require("./TokenMarket/CrowdsaleToken.sol");
var EthTranchePricing = artifacts.require("./TokenMarket/EthTranchePricing.sol");
var MultiSigWallet = artifacts.require("./zeppelinTokenMarket/MultiSigWallet.sol");
var MintedEthCappedCrowdsale = artifacts.require("./TokenMarket/MintedEthCappedCrowdsale.sol");

module.exports = function(deployer) {
    deployer.deploy(SafeMathLib);
    deployer.link(SafeMathLib, CrowdsaleToken);
    deployer.link(SafeMathLib, EthTranchePricing);
    deployer.link(SafeMathLib, MultiSigWallet);
    deployer.link(SafeMathLib, MintedEthCappedCrowdsale);

    deployer.deploy(CrowdsaleToken, "TokenI", "TI", 1000, 2, true).then(function() {
        deployer.deploy(EthTranchePricing, [100, 7, 1000, 0]).then(function() { // last tranche price must be zero, terminating the crowdale
            deployer.deploy(MultiSigWallet, [0x4cdabc27b48893058aa1675683af3485e4409eff], false, 100). then(function() {
                deployer.deploy(MintedEthCappedCrowdsale,
                    CrowdsaleToken.address, // _token 
                    EthTranchePricing.address, // _pricingStrategy
                    MultiSigWallet.address, // _multisigWallet 
                    1498867200, // _start (the UNIX timestamp start date of the crowdsale)
                    1500000000, // _end
                    1000, // _minimumFundingGoal
                    1000000000 // _weiCap (maximum amount of wei this crowdsale can raise)
                    );
            });
        });
    });
};