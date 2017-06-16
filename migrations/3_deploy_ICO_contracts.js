var SafeMathLib = artifacts.require("./SafeMathLib.sol");
var CrowdsaleToken = artifacts.require("./CrowdsaleToken.sol");
var FlatPricing = artifacts.require("./FlatPricing.sol");
var MultiSigWallet = artifacts.require("./MultiSigWallet.sol");
var MintedEthCappedCrowdsale = artifacts.require("./MintedEthCappedCrowdsale.sol");
var BonusFinalizeAgent = artifacts.require("./BonusFinalizeAgent.sol");

// TODO: adapt to client needs
var TOKEN_NAME = "TokenI";
var TOKEN_SYMBOL = "TI";
var INITIAL_SUPPLY = 1000;
var DECIMALS = 2;
var MINTABLE = true;
var PRICE = 500;
var START_DATE = 1498867200;
var END_DATE = 1500000000;
var MINIMUM_FUNDING_GOAL = 1000;
var WEI_CAP = 1000000000;
var BONUS_BASE_POINTS = 300000; // equivalent to 30%

module.exports = function(deployer) {
    deployer.deploy(SafeMathLib);
    deployer.link(SafeMathLib, CrowdsaleToken);
    deployer.link(SafeMathLib, FlatPricing);
    deployer.link(SafeMathLib, MintedEthCappedCrowdsale);
    deployer.link(SafeMathLib, BonusFinalizeAgent);

    deployer.deploy(CrowdsaleToken,
        TOKEN_NAME,
        TOKEN_SYMBOL,
        INITIAL_SUPPLY,
        DECIMALS,
        MINTABLE)
    .then(function() {
        deployer.deploy(FlatPricing, PRICE)
        .then(function() {
            // TODO: change to use client's MultiSigWallet
            deployer.deploy(MultiSigWallet, [0x4cdabc27b48893058aa1675683af3485e4409eff], 1)
            .then(function() {
                deployer.deploy(MintedEthCappedCrowdsale,
                    CrowdsaleToken.address, 
                    FlatPricing.address, 
                    MultiSigWallet.address,
                    START_DATE, 
                    END_DATE, 
                    MINIMUM_FUNDING_GOAL, 
                    WEI_CAP)
                .then(function() {
                    deployer.deploy(BonusFinalizeAgent,
                        CrowdsaleToken.address,
                        MintedEthCappedCrowdsale.address,
                        BONUS_BASE_POINTS,
                        MultiSigWallet.address)
                    .then(function() {
                        MintedEthCappedCrowdsale.deployed().then(function(crowdsale) {
                            crowdsale.setFinalizeAgent(BonusFinalizeAgent.address);
                            crowdsale.transferOwnership(MultiSigWallet.address);
                        });
                        CrowdsaleToken.deployed().then(function(token) {
                            token.setMintAgent(MintedEthCappedCrowdsale.address, true);
                            token.setMintAgent(BonusFinalizeAgent.address, true);
                            token.setReleaseAgent(BonusFinalizeAgent.address);
                            token.transferOwnership(MultiSigWallet.address);
                        });
                    });
                });
            });
        });
    });
};