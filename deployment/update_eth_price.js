const Web3 = require("web3");
const web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
// const web3 = new Web3(new Web3.providers.IpcProvider(config.ipc_file, net));

const cs_abi = require("./Crowdsale.abi.js");
const account = "0x54d9249C776C56520A62faeCB87A00E105E8c9Dc";

// Setup contract objects
const CS_contract = web3.eth.contract(cs_abi);
CS_instance = CS_contract.at("0xb9aC67A866b2e6990538ad5C9c20b830E5404518")

new_rate = 900 * 1000;

CS_instance.updateEursPerEth(new_rate, {from: account, gasPrice: 10000000000, gas: 200000});
