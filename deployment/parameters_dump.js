const Web3 = require("web3");
const web3 = new Web3(new Web3.providers.HttpProvider("http://localhost:8545"));
// const web3 = new Web3(new Web3.providers.IpcProvider(config.ipc_file, net));
const config = require("../config.js")(web3, "liveNet");

console.log("Web3 version:", web3.version.api)

console.log(
  "Ether in EUR:", config.ether_in_eur.toString(),
  "\n\nMultisig address:", config.MW_address, 
  "\n\nStart time:", config.startTime, 
  "\n\nEnd time:", config.endTime, 
  "\n\nToken retriever: set in the deployment script\n"
); 
for(i = 0; i < config.tranches.length/4; i++) {
  console.log("Tranche #", i, " -----------------------------------------------------------------",
    "\nTokens cap:    ", config.tranches[4*i].dividedBy(10**18).toExponential(),
    "\nStart:         ", (new Date(config.tranches[4*i+1]*1000)).toGMTString(), 
    "\nEnd:           ", (new Date(config.tranches[4*i+2]*1000)).toGMTString(),
    "\nTokens per EUR:", config.tranches[4*i+3].toExponential()
  );
}
console.log("------------------------------------------------------------------------------");
console.log("\nTransaction sender: set in the deployment script",
            "\n Gas and Gas price: set in the deployment script"
);