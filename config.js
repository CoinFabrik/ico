var config = {};

config.tokenName = 'BurgerKoenig';
config.tokenSymbol = 'BK';
config.initialSupply = 0; // in ether
config.decimals = 8;
config.mintable = true;
config.price = 0.001; // in ethert
config.startDate = (new Date().getTime()/1000) | 0; //1500645594 + 180 //
config.endDate = config.startDate + 3600*48; // bla
config.minimumFundingGoal = 5; // in ether (CHANGE to USD 4m)
config.bonusBasePoints = 3000; // equivalent to 30%
config.chunkedMultipleCap = 25; // in ether (CHANGE to USD 5m)
config.limitPerAddress = 6; // for testing; in ether

module.exports = config;
