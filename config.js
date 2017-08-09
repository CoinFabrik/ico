var config = {};

config.tokenName = 'Hubiits';
config.tokenSymbol = 'HB'; // TODO: check if this is the correct symbol
// 9/8/2017 20:56 UTC block number: 4,137,656
// 17/8/2017 ~0:00 UTC block number offset: 28,239 at 21.8 seconds per block on average
config.startBlock = 4137656 + 28239
// We give two week's worth of blocks for the crowdsale to run its course: 55,486
config.endBlock = config.startBlock + 55486

// These are not used anymore
config.initialSupply = 0; // in ether
config.decimals = 8;
config.mintable = true;
config.price = (1/500) * (10 ** config.decimals); // how many tokens in E-8 notation per wei
config.startDate = (((new Date()).getTime()/1000) | 0) + 3600; //1500645594 + 180 //
config.endDate = config.startDate + 3600*48;
config.minimumFundingGoal = 5; // in ether (CHANGE to USD 4m)
config.bonusBasePoints = 3000; // equivalent to 30%
config.chunkedMultipleCap = 10; // in ether (CHANGE to USD 5m)
config.limitPerAddress = 6; // for testing; in ether

module.exports = config;
