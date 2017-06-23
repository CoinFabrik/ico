var MintedEthCappedCrowdsale = artifacts.require("./MintedEthCappedCrowdsale.sol");
var CrowdsaleToken = artifacts.require("./CrowdsaleToken.sol");
var MysteriumToken = artifacts.require("./MysteriumToken.sol");

contract('Mysterium Upgrade', function(accounts) {
  // it("Initial check", function() {
  //   var crowdsale;
  //   var token;
  //   return Promise.all([
  //     MintedEthCappedCrowdsale.deployed(),
  //     CrowdsaleToken.deployed()
  //   ]).then(function([crowdsaleInstance, tokenInstance]) {
  //     crowdsale = crowdsaleInstance;
  //     token = tokenInstance;
  //     return crowdsale.getState.call();
  //   }).then(function(state) {
  //     // console.log(state.toNumber());
  //     assert.equal(state.valueOf(), 3, "Should be in funding");
  //   });
  // });
  // it("Funding Params", function() {
  //   var crowdsale;
  //   var token;
  //   return Promise.all([
  //     MintedEthCappedCrowdsale.deployed(),
  //     CrowdsaleToken.deployed()
  //   ]).then(function([crowdsaleInstance, tokenInstance]) {
  //     crowdsale = crowdsaleInstance;
  //     token = tokenInstance;
  //     return Promise.all([
  //         crowdsale.getState.call(),
  //         crowdsale.startsAt.call(),
  //         crowdsale.endsAt.call(),
  //         crowdsale.weiCap.call(),
  //         crowdsale.weiRaised.call(),
  //     ]);
  //   }).then(function([state, startsAt, endsAt, weiCap, weiRaised]) {
  //     //console.log(state.toNumber());
  //     //console.log(startsAt.toNumber());
  //     //console.log(endsAt.toNumber());
  //     //console.log(weiCap.toNumber());
  //     //console.log(weiRaised.toNumber());
  //     assert.equal(state.valueOf(), 3, "Should be in funding stage");
  //     assert.equal(weiCap.valueOf(), 1000, "Should have 1000 in cap");
  //     assert.equal(weiRaised.valueOf(), 0, "Should have raised 0");
  //   });
  // });
  // it("Funding", function() {
  //   var crowdsale;
  //   var token;
  //   return Promise.all([
  //     MintedEthCappedCrowdsale.deployed(),
  //     CrowdsaleToken.deployed()
  //   ]).then(function([crowdsaleInstance, tokenInstance]) {
  //     crowdsale = crowdsaleInstance;
  //     token = tokenInstance;
  //     return token.balanceOf(accounts[1]);
  //   }).then(function(balance) {
  //     assert.equal(balance.valueOf(), 0, "Should not have balance");
  //     return crowdsale.buy({ from: accounts[1], value: 100 });
  //   }).then(function() {
  //     return token.balanceOf(accounts[1]);
  //   }).then(function(balance) {
  //     assert.equal(balance.valueOf(), 100, "Should be 100 in funding");
  //   });
  // });
  // it("Funded", function() {
  //   var crowdsale;
  //   var token;
  //   var idxs = [];
  //   for (var i=0; i<5; ++i) {
  //     idxs.push(i);
  //     idxs.push(i);
  //   }
  //   return Promise.all([
  //     MintedEthCappedCrowdsale.deployed(),
  //     CrowdsaleToken.deployed()
  //   ]).then(function([crowdsaleInstance, tokenInstance]) {
  //     crowdsale = crowdsaleInstance;
  //     token = tokenInstance;
  //     return Promise.all(idxs.map((i) => crowdsale.buy({ from: accounts[i], value: 100 })));
  //   }).then(function() {
  //     return crowdsale.getState.call();
  //   }).then(function(state) {
  //     assert.equal(state.valueOf(), 4, "Should be success");
  //   //  return Promise.all(idxs.map((i) => token.balanceOf(accounts[i])));
  //   //}).then(function(balances) {
  //   //  assert.equal(balances[0].valueOf(), 100, "Should be 100 in funding");
  //     return crowdsale.finalize();
  //   }).then(function() {
  //     return crowdsale.finalized.call();
  //   }).then(function(finalized) {
  //     assert.equal(finalized, true, "Should be finalized");
  //   });
  // });
  it("Upgrade", function() {
    var crowdsale;
    var token;
    var upgradeToken;
    var idxs = [];
    for (var i=1; i<=5; ++i) {
      idxs.push(i);
    }
    return Promise.all([
      MintedEthCappedCrowdsale.deployed(),
      CrowdsaleToken.deployed(),
      MysteriumToken.deployed(),
    ]).then(function([crowdsaleInstance, tokenInstance, upgradeTokenInstance]) {
      crowdsale = crowdsaleInstance;
      token = tokenInstance;
      upgradeToken = upgradeTokenInstance;
      return Promise.all(idxs.map((i) => crowdsale.buy({ from: accounts[i], value: 200 })));
    }).then(function() {
      return crowdsale.getState.call();
    }).then(function(state) {
      assert.equal(state.valueOf(), 4, "Should be success");
      return crowdsale.finalize();
    }).then(function() {
      return Promise.all([
        token.getUpgradeState.call(),
        token.totalSupply.call(),
        upgradeAgent.originalSupply.call(),
      ]);
    }).then(function([upgradeState, totalSupply, originalSupply]) {
      assert.equal(upgradeState.valueOf(), 2, "Should be waiting for upgrade");
      assert.equal(totalSupply.valueOf(), 1000, "Token supply should be 1000");
      assert.equal(originalSupply.valueOf(), 1000, "Original token supply should be 1000");
      return upgradeToken.setOriginaryToken(CrowdsaleToken.address);
    }).then(function() {
      return token.setUpgradeAgent(MysteriumToken.address);
    }).then(function() {
      return token.getUpgradeState.call();
    }).then(function(upgradeState) {
      assert.equal(upgradeState.valueOf(), 3, "Should be ready to upgrade");
      return token.upgrade(200, { from: accounts[1] });
    }).then(function() {
      return Promise.all([
        token.balanceOf.call(accounts[1]),
        upgradeToken.balanceOf.call(accounts[1]),
        token.getUpgradeState.call()
      ]);
    }).then(function([originalBalance, upgradedBalance, upgradeState]) {
      assert.equal(originalBalance.valueOf(), 0, "Should have balance of 0");
      assert.equal(upgradedBalance.valueOf(), 200, "Should have a balance of 200");
      assert.equal(upgradeState.valueOf(), 4, "Should be upgrading");
    });
  });
});
