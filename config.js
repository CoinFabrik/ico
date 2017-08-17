var config = {};

const Web3 = require("web3");
const web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));

//Neededto initialize the crowdsale
config.MW_address = "0x931F6E5c89dD5559D3820cFBd1975BA5d92F8777";
config.startBlock = web3.eth.getBlock("latest").number + 50;
config.endBlock = config.startBlock + 1000;
config.fundingCap = web3.toWei("180000");


//Needed in order to initialize the token
config.tokenName = 'Hubiits';
config.tokenSymbol = 'HBT';
config.initialSupply = 0; // in ether
config.decimals = 15;
config.mintable = true;

module.exports = config;