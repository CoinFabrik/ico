const Web3 = require("web3");
const web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
// const web3 = new Web3(new Web3.providers.IpcProvider(config.ipc_file, net));
const config = require("../config.js")(web3, "privateTestnet");

console.log("Web3 version:", web3.version.api)

console.log(
  //"MiliEURs per Eth:", config.milieurs_per_eth.toString(),
  "\n\nMultisig address:", config.multisig_owners, 
  "\n\nStart time:", (new Date(config.startTime*1000)).toGMTString(),
  "\n\nEnd time:", (new Date(config.endTime*1000)).toGMTString(),
  "\n\nToken retriever: set in the deployment script\n"
); 
for(i = 0; i < config.tranches.length/4; i++) {
  console.log("Tranche #", i, " -----------------------------------------------------------------",
    "\nFullTokens cap:", config.tranches[4*i].dividedBy(10**18).toExponential(),
    "\nStart:         ", (new Date(config.tranches[4*i+1]*1000)).toGMTString(), 
    "\nEnd:           ", (new Date(config.tranches[4*i+2]*1000)).toGMTString(),
    "\nTokens per EUR:", config.tranches[4*i+3].toExponential()
  );
}
console.log("------------------------------------------------------------------------------");
console.log("\nTransaction sender: set in the deployment script",
            "\n Gas and Gas price: set in the deployment script"
);
