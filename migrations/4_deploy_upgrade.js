var SafeMath = artifacts.require("./SafeMath.sol");
var CrowdsaleToken = artifacts.require("./CrowdsaleToken.sol");
var MintedEthCappedCrowdsale = artifacts.require("./MintedEthCappedCrowdsale.sol");
var MysteriumToken = artifacts.require("./MysteriumToken.sol");


var TOKEN_NAME = "Mysterium";
var TOKEN_SYMBOL = "MIST";
var INITIAL_SUPPLY = 1000;
var DECIMALS = 2;

var crowdsale;
var token;
var upgradeToken;


module.exports = function(deployer) {
    deployer.deploy(SafeMath);
    deployer.link(SafeMath, MysteriumToken);

    deployer.deploy(MysteriumToken,
        TOKEN_NAME,
        TOKEN_SYMBOL,
        INITIAL_SUPPLY,
        DECIMALS
    ).then(function() {
        return MysteriumToken.deployed();
    }).then(function(instance) {
        upgradeToken = instance;
    });
};
