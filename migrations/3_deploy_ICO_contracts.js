var SafeMath = artifacts.require("./SafeMath.sol");
var MultiSigWallet = artifacts.require("./MultiSigWallet.sol");
var FlatPricing = artifacts.require("./FlatPricing.sol");
var BonusFinalizeAgent = artifacts.require("./BonusFinalizeAgent.sol");
var CrowdsaleToken = artifacts.require("./CrowdsaleToken.sol");
var MintedEthCappedCrowdsale = artifacts.require("./MintedEthCappedCrowdsale.sol");

// TODO: adapt to client needs
var TOKEN_NAME = "TokenI";
var TOKEN_SYMBOL = "TI";
var INITIAL_SUPPLY = 1000;
var DECIMALS = 2;
var MINTABLE = true;
var PRICE = 500;
var START_DATE = 1498867200;
var END_DATE = 1500000000;
var MINIMUM_FUNDING_GOAL = 2000;
var WEI_CAP = 3000;
var BONUS_BASE_POINTS = 300000; // equivalent to 30%

module.exports = function(deployer) {
    deployer.deploy(SafeMath);
    deployer.link(SafeMath, FlatPricing);
    deployer.link(SafeMath, BonusFinalizeAgent);
    deployer.link(SafeMath, CrowdsaleToken);
    deployer.link(SafeMath, MintedEthCappedCrowdsale);

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
                        MintedEthCappedCrowdsale.deployed()
                        .then(function(crowdsale) {
                            crowdsale.setFinalizeAgent(BonusFinalizeAgent.address)
                            .then(function() {
                                crowdsale.transferOwnership(MultiSigWallet.address)
                                .catch(function(error1) {
                                    console.log('Failed to transfer crowdsale contract\'s ownership', error1);
                                });
                            })
                            .catch(function(error2) {
                                console.log('Failed to set a finalize agent for crowdsale contract', error2);
                            });
                        });
                        CrowdsaleToken.deployed()
                        .then(function(token) {
                            token.setMintAgent(MintedEthCappedCrowdsale.address, true)
                            .then(function() {
                                token.setMintAgent(BonusFinalizeAgent.address, true)
                                .then(function() {
                                    token.setReleaseAgent(BonusFinalizeAgent.address)
                                    .then(function() {
                                        token.transferOwnership(MultiSigWallet.address)
                                        .catch(function(error3) {
                                            console.log('Failed to transfer token contract\'s ownership', error3);
                                        });
                                    })
                                    .catch(function(error4) {
                                        console.log('Failed to set a release agent for token contract', error4);
                                    });
                                })
                                .catch(function(error5) {
                                    console.log('Failed to set a mint agent (BonusFinalizeAgent) for token contract', error5);
                                });
                            })
                            .catch(function(error6) {
                                console.log('Failed to set a mint agent (MintedEthCappedCrowdsale) for token contract', error6);
                            });
                        })
                        .catch(function(error7) {
                            console.log('Failed to deploy token contract', error7);
                        });
                    })
                    .catch(function(error8) {
                        console.log('Failed to deploy finalize agent contract', error8);
                    });
                })
                .catch(function(error9) {
                    console.log('Failed to deploy crowdsale contract', error9);
                });
            })
            .catch(function(error10) {
                console.log('Failed to deploy multisig wallet contract', error10);
            });
        })
        .catch(function(error11) {
            console.log('Failed to deploy pricing strategy contract', error11);
        });
    })
    .catch(function(error12) {
        console.log('Failed to deploy token contract', error12);
    });
};