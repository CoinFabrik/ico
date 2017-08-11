var config = {};
config.tests = {};

const Web3 = require("web3");
const web3 = new Web3(new Web3.providers.HttpProvider("http://192.168.0.186:7999"));

config.tokenName = 'Hubiits';
config.tokenSymbol = 'HB'; // TODO: check if this is the correct symbol
// 9/8/2017 20:56 UTC block number: 4,137,656
// 17/8/2017 ~0:00 UTC block number offset: 28,239 at 21.8 seconds per block on average
config.startBlock = 4137656 + 28239
// We give two week's worth of blocks for the crowdsale to run its course: 55,486
config.endBlock = config.startBlock + 55486

config.tests.startBlock = web3.eth.getBlock("latest").number + 10;
config.tests.endBlock = config.tests.startBlock + 500;

module.exports = config;
