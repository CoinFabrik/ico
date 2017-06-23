var MintedEthCappedCrowdsale = artifacts.require("./MintedEthCappedCrowdsale.sol");
var CrowdsaleToken = artifacts.require("./CrowdsaleToken.sol");
var MysteriumToken = artifacts.require("./MysteriumToken.sol");

contract('Mysterium Upgrade', function(accounts) {
  var crowdsale;
  var token;
  var upgradeToken;
  var idxs = [];
  for (var i=1; i<=5; ++i) {
    idxs.push(i);
  }

  it("Check contracts deploy", function() {
    return Promise.all([
      MintedEthCappedCrowdsale.deployed(),
      CrowdsaleToken.deployed(),
      MysteriumToken.deployed(),
    ]).then(function([crowdsaleInstance, tokenInstance, upgradeTokenInstance]) {
      crowdsale = crowdsaleInstance;
      token = tokenInstance;
      upgradeToken = upgradeTokenInstance;
    }).then(function() {
      return crowdsale.getState.call();
    }).then(function(state) {
      assert.equal(state.valueOf(), 3, "Crowdsale should be in funding stage");
    });
  });

  it("Fund crowdsale", function() {
    return Promise.all(idxs.map((i) => crowdsale.buy({ from: accounts[i], value: 200 })))
    .then(function() {
      return crowdsale.getState.call();
    }).then(function(state) {
      assert.equal(state.valueOf(), 4, "Crowdsale should be in success stage");
      return crowdsale.finalize();
    }).then(function() {
      return Promise.all([
        crowdsale.finalized.call(),
        token.getUpgradeState.call(),
        token.totalSupply.call(),
      ]);
    }).then(function([finalized, upgradeState, totalSupply]) {
      assert.equal(finalized, true, "Crowdsale should have finalized");
      assert.equal(upgradeState.valueOf(), 2, "Token should be waiting for upgrade");
      assert.equal(totalSupply.valueOf(), 1000, "Token supply should be 1000");
    });
  });

  it("Set token upgrade agent", function() {
    return upgradeToken.setOriginaryToken(CrowdsaleToken.address)
    .then(function() {
      return token.setUpgradeAgent(MysteriumToken.address);
    }).then(function() {
      return token.getUpgradeState.call();
    }).then(function(upgradeState) {
      assert.equal(upgradeState.valueOf(), 3, "Token should be ready to upgrade");
    });
  });

  it("Upgrade tokens", function() {
    return token.upgrade(200, { from: accounts[1] })
    .then(function() {
      return Promise.all([
        token.balanceOf.call(accounts[1]),
        upgradeToken.balanceOf.call(accounts[1]),
        token.getUpgradeState.call()
      ]);
    }).then(function([originalBalance, upgradedBalance, upgradeState]) {
      assert.equal(originalBalance.valueOf(), 0, "Old token should have balance of 0");
      assert.equal(upgradedBalance.valueOf(), 200, "New token should have a balance of 200");
      assert.equal(upgradeState.valueOf(), 4, "Token should be upgrading");
    });
  });
});
