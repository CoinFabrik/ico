const Web3 = require("web3");
const web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
// const web3 = new Web3(new Web3.providers.IpcProvider(config.ipc_file, net));
console.log(web3)
console.log(web3.BigNumber)
const config = require("../config.js")(web3, "liveNet");

const cs_abi = require("./Crowdsale.abi.js");
const cs_bytecode = require("./Crowdsale.bin.js");

const account = "0x54d9249C776C56520A62faeCB87A00E105E8c9Dc";

// Setup contract objects
const CS_contract = web3.eth.contract(cs_abi);



//const crowdsale = CS_contract.new(config.ether_in_eur, config.MW_address, config.startTime, config.endTime, accounts[1], config.tranches, {from: account, data: "0x" + cs_bytecode, gasPrice: 1000000000, gas: 5000000});

