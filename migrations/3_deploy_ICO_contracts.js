var SafeMath = artifacts.require("./SafeMath.sol");
var MultiSigWallet = artifacts.require("./MultiSigWallet.sol");
var FlatPricing = artifacts.require("./FlatPricing.sol");
var BonusFinalizeAgent = artifacts.require("./BonusFinalizeAgent.sol");
var CrowdsaleToken = artifacts.require("./CrowdsaleToken.sol");
var MintedEthCappedCrowdsale = artifacts.require("./MintedEthCappedCrowdsale.sol");

// TODO: adapt to client needs
var TOKEN_NAME = "Mysterium";
var TOKEN_SYMBOL = "MIST";
var INITIAL_SUPPLY = 0;
var DECIMALS = 2;
var MINTABLE = true;
var PRICE = 100;
var START_DATE = 1498003200;
var END_DATE = 1498089600;
var MINIMUM_FUNDING_GOAL = 100;
var WEI_CAP = 1000;
var BONUS_BASE_POINTS = 300000; // equivalent to 30%

var wallet = "0xb8873fc3e5372cca6cd1e20cfeb77a2b322d59b5";

var crowdsale;
var token;

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
        return deployer.deploy(FlatPricing, PRICE);
    }).then(function() {
        return deployer.deploy(MintedEthCappedCrowdsale,
            CrowdsaleToken.address,
            FlatPricing.address,
            wallet,
            START_DATE,
            END_DATE,
            MINIMUM_FUNDING_GOAL,
            WEI_CAP);
    }).then(function() {
        return deployer.deploy(BonusFinalizeAgent,
            CrowdsaleToken.address,
            MintedEthCappedCrowdsale.address,
            BONUS_BASE_POINTS,
            wallet);
    }).then(function() {
        return MintedEthCappedCrowdsale.deployed();
    }).then(function(instance) {
        crowdsale = instance;
        return crowdsale.setFinalizeAgent(BonusFinalizeAgent.address);
    }).then(function() {
        return CrowdsaleToken.deployed();
    }).then(function(instance) {
        token = instance;
        return token.setMintAgent(MintedEthCappedCrowdsale.address, true);
    }).then(function() {
        return token.setMintAgent(BonusFinalizeAgent.address, true)
    }).then(function() {
        return token.setReleaseAgent(BonusFinalizeAgent.address);
    }).catch(function(error12) {
        console.log('Failed to deploy token contract', error12);
    });
};
