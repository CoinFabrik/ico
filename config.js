var config = {};

const Web3 = require("web3");
const web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));

config.tokenName = 'Hubiits';
config.tokenSymbol = 'HB'; // TODO: check if this is the correct symbol

// 9/8/2017 20:56 UTC block number: 4,137,656
// 17/8/2017 ~0:00 UTC block number offset: 28,239 at 21.8 seconds per block on average

config.startBlock = web3.eth.getBlock("latest").number + 50;
// We give two week's worth of blocks for the crowdsale to run its course: 55,486
config.endBlock = config.startBlock + 1000;

// These are not used anymore
config.initialSupply = 0; // in ether
config.decimals = 15;
config.mintable = true;
config.price = (1/500) * (10 ** config.decimals); // how many tokens in E-8 notation per wei

config.MW_address = "0x931F6E5c89dD5559D3820cFBd1975BA5d92F87E9";
module.exports = config;
