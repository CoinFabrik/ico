var config = {};

config.tokenName = 'Hubii';
config.tokenSymbol = 'HI';
config.initialSupply = 0; // in ether
config.decimals = 8;
config.mintable = true;
config.price = 0.001; // in ethert
//SET TIME CORRECLTY FOR GOD SAKE	
config.startDate = Date.now()/1000 | 0; //1500645594 + 180 //
config.endDate = 1501772400; // bla
config.minimumFundingGoal = 5; // in ether (CHANGE to USD 4m)
config.bonusBasePoints = 3000; // equivalent to 30%
config.chunkedMultipleCap = 40; // in ether (CHANGE to USD 5m)
config.limitPerAddress = 7; // for testing; in ether

module.exports = config;