//Load modules
var fs = require("fs");
var solc = require('solc');
var Web3 = require('web3');
var net = require('net');

//Instantiate variables
var gasEstimated;
var gasPriceEstimated;
var contractInstance;
var contractAddress;
var mainAddress;

//Address that will handle tokens trapped in the contract
var tokenRetrieverAccount = "0x0F048ff7dE76B83fDC14912246AC4da5FA755cFE";

//Connect to the private node
var web3 = new Web3(new Web3.providers.IpcProvider('/home/coinfabrik/Programming/blockchain/node/geth.ipc', net));

//Import params into config variable
var config = require("../config.js")(web3, "privateTestnet");

//Read abi and bytecode from files
var abi = require("./Crowdsale.abi.js");
var bytecode = require("./Crowdsale.bin.js");

function getAccount(){
  web3.eth.getAccounts(function(error, result) {
    if(error != null) {
      console.log("Couldn't get accounts");
    }
    else {
      mainAddress = result[0];
    }
  })
}

getAccount();

//Create contract instance
var crowdsaleContract = new web3.eth.Contract(abi, {
   from: mainAddress,
   gasPrice: 2000000000000000000,
   gas: 4700000,
   data: bytecode
 });

//Find estimated gas price for operation
web3.eth.getGasPrice().then((averageGasPrice) => {
  console.log("Average gas price: " + averageGasPrice);
  gasPriceEstimated = averageGasPrice;
}).catch(console.error);

function deployContract(){

  console.log("The address of Mathias account is: " + mainAddress);
  //crowdsaleContract.deploy({ arguments: [config.multisig_owners[0], config.startTime, config.endTime, account, config.tranches] }).estimateGas(function(err, gas){
  //  console.log("Estimated gas: " + gas);
  //  gasEstimated = gas;
  //});

  crowdsaleContract.deploy({ arguments: [config.multisig_owners[0], config.startTime, config.endTime, tokenRetrieverAccount, config.tranches] }).send({
      from: mainAddress,
      gasPrice: gasPriceEstimated, 
      gas: 47000000000
  }).then(function(instance) {
      console.log(instance.options.address);
      contractInstance = instance;
      contractAddress = instance.options.address;
  });
}

setTimeout(deployContract, 20);