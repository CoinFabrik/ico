var config = {};
config.tests = {};

const Web3 = require("web3");
const web3 = new Web3(new Web3.providers.HttpProvider("http://192.168.0.186:7999"));

// 9/8/2017 20:56 UTC block number: 4,137,656
// 17/8/2017 ~0:00 UTC block number offset: 28,239 at 21.8 seconds per block on average
// 19/8/2017 17:58 UTC block number: 4,178,454
// 24/8/2017 ~15:00 UTC block number offset: 19,867
config.startBlock = 4178454 + 19867;
// We give two week's worth of blocks for the crowdsale to run its course: 57,056
config.endBlock = config.startBlock + 57056;
config.MW_address = "0x931F6E5c89dD5559D3820cFBd1975BA5d92F8777";
// This is our multisig wallet in mainnet that we use for testing.
config.tests.MW_address = "0x8ffc991fc4c4fc53329ad296c1afe41470cffbb3";
config.fundingCap = web3.toWei("180000");

config.multisig_owners = ["0xf19258256b06324c7516b00bf5c76af001ee1e95"];

config.tests.startBlock = web3.eth.getBlock("latest").number + 10;
config.tests.endBlock = config.tests.startBlock + 500;

module.exports = config;
