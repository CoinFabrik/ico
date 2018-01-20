const Web3 = require("web3");
const web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));

const cs_abi = require("./Crowdsale.abi.js");

const account = "0x54d9249C776C56520A62faeCB87A00E105E8c9Dc";

// Setup contract objects
const CS_contract = web3.eth.contract(cs_abi);

const CS_instance = CS_contract.at("0xb9aC67A866b2e6990538ad5C9c20b830E5404518");

CS_instance.setRequireSignedAddress(true, "0x9773cc14E40853917B9a8fB49de4ABdEa736ED1E", {from: account, gasPrice: 3000000000, gas:200000, nonce: 1451});
