var Migrations = artifacts.require("./Migrations.sol");

module.exports = function(deployer, network, accounts) {
  if (network != "test") return;
  deployer.deploy(Migrations, {gas: 200000});
};
