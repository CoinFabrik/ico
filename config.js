var config = {};

// TODO: adapt to client needs
config.TOKEN_NAME = 'Hubii';
config.TOKEN_SYMBOL = 'HI';
config.INITIAL_SUPPLY = 1000;
config.DECIMALS = 2;
config.MINTABLE = true;
config.PRICE = 500;
config.START_DATE = 1500562800; // 20th July 8am PDT
config.END_DATE = 1501772400; // 2 weeks later
config.MINIMUM_FUNDING_GOAL = 1; // CHANGE to USD 4m. Value is in wei.
config.BONUS_BASE_POINTS = 300000; // equivalent to 30%
config.CHUNKED_MULTIPLE_CAP = 500; // in ether
config.LIMIT_PER_ADDRESS = 1000; // in ether

module.exports = config;