var SafeMathLib = artifacts.require("./Monaco/SafeMathLib.sol");
var CrowdsaleToken = artifacts.require("./Monaco/CrowdsaleToken.sol");
var EthTranchePricing = artifacts.require("./Monaco/EthTranchePricing.sol");
var MultiSigWallet = artifacts.require("./Monaco/MultiSigWallet.sol");
var MintedEthCappedCrowdsale = artifacts.require("./Monaco/MintedEthCappedCrowdsale.sol");

module.exports = function(deployer) {
    deployer.deploy(SafeMathLib);
    deployer.link(SafeMathLib, CrowdsaleToken);
    deployer.link(SafeMathLib, EthTranchePricing);
    deployer.link(SafeMathLib, MintedEthCappedCrowdsale);

    deployer.deploy(CrowdsaleToken, "TokenI", "TI", 1000, 2, true) // string _name, string _symbol, uint _initialSupply, uint _decimals, bool _mintable
    .then(function() {
        deployer.deploy(EthTranchePricing, [0, 2, 1000, 4, 10000, 0]) // uint[] _tranches (check EthTranchePricing for restrictions)
        .then(function() {
            deployer.deploy(MultiSigWallet, [0x92ac5d12df3e3b89f8cedcc0a1d599c2aea0f977, 0x5feef421e63ae269d31ddabea8fcc729ab516a76], 2) // address[] _owners, uint _required
            .then(function() {
                deployer.deploy(MintedEthCappedCrowdsale,
                    CrowdsaleToken.address, // address _token
                    EthTranchePricing.address, // _PricingStrategy _pricingStrategy
                    MultiSigWallet.address, // address _multiSigWallet
                    1498867200, // uint _start (the UNIX timestamp start date of the crowdsale)
                    1500000000, // uint _end
                    1000, // uint _minimumFundingGoal
                    1000000000 // uint _weiCap (maximum amount of wei this crowdsale can raise)
                    );
            });
        });
    });
};