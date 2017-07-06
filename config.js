var config = {};

config.tokenName = 'Hubii';
config.tokenSymbol = 'HI';
config.initialSupply = 0; // in ether
config.decimals = 8;
config.mintable = true;
config.price = 0.001; // in ether
config.startDate = 1500562800; // 20th July 8am PDT
config.endDate = 1501772400; // 2 weeks later
config.minimumFundingGoal = 50; // in ether (CHANGE to USD 4m)
config.bonusBasePoints = 3000; // equivalent to 30%
config.chunkedMultipleCap = 500; // in ether (CHANGE to USD 5m)
config.limitPerAddress = 10000; // in ether

module.exports = config;