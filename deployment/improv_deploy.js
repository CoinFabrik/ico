const Web3 = require("web3");
const web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
// const web3 = new Web3(new Web3.providers.IpcProvider(config.ipc_file, net));

const config = require("../config.js")(web3, "liveNet");

const cs_abi = require("./Crowdsale.abi.js");
const cs_bytecode = require("./Crowdsale.bin.js");

const account = "0x54d9249C776C56520A62faeCB87A00E105E8c9Dc";

// Setup contract objects
const CS_contract = web3.eth.contract(cs_abi);
const crowdsale = CS_contract.new(config.milieurs_per_eth, config.MW_address, config.startTime, config.endTime, account, config.tranches, {from: account, data: "0x" + cs_bytecode, gasPrice: 10000000000, gas: 4800000});
