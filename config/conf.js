Web3 = require('web3');
web3 = new Web3();

// TODO: adapt to client needs
exports.TOKEN_NAME = 'TokenI';
exports.TOKEN_SYMBOL = 'TI';
exports.INITIAL_SUPPLY = 1000;
exports.DECIMALS = 2;
exports.MINTABLE = true;
exports.PRICE = 500;
exports.START_DATE = 1498867200;
exports.END_DATE = 1500000000;
exports.MINIMUM_FUNDING_GOAL = 2000;
exports.BONUS_BASE_POINTS = 300000; // equivalent to 30%


exports.CURVES = [
    [web3.toWei(3), 30, 10**12],
    [web3.toWei(8), 30, 10**12],
    [web3.toWei(15), 30, 10**12],
];
exports.NUM_HIDDEN_CURVES = 7;
