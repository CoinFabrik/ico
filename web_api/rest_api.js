const abi = require("./contracts_abi.js");
const config = require("./config.js");
const net = require("net");
const Web3 = require("web3");
const express = require("express");
const cors = require("cors");
const app = express();
// const fs = require('fs');

// const web3 = new Web3(new Web3.providers.IpcProvider(config.ipc_file, net));
const web3 = new Web3(new Web3.providers.HttpProvider(config.nodeIpPort));

// Setup contract objects
const CS_contract = web3.eth.contract(abi.Crowdsale);
const crowdsale = CS_contract.at(config.crowdsale.address);

// local cache
let last_block_queried;
let cached_state;
// let original_page = fs.readFileSync("../front/index.html", {encoding:'utf8'});


// const cors_options = { origin: [ "https://banx.network", "https://www.banx.network" ] };
// app.use(cors(cors_options));
app.options("*", cors());
app.use(express.static("../web_test"));

// Defined to avoid waiting on database or blockchain node to respond
app.head("/", (request, response) => {
  response.status(200);
  response.type("json");
});

app.get("/", (request, response) => {
  response.status(200);
  if (request.query.method != "query_crowdsale") {
    response.json({"error": "Method requested is not supported."});
    return;
  }
  response.json(cached_state);
  // if (request.query.method == "query_crowdsale") {
  //   response.json(cached_state);
  // } else if (request.query.method === undefined) {
  //   response.send(cached_page);
  // }
});

app.listen(8080);

const callback_generator = function (resolve, reject) {
  return (error, value) => {
    if (error) {
      reject(error);
    } else {
      resolve(value);
    }
  };
};

// Promisify a web3 asynchronous call (this becomes unnecessary as soon as web3 promisifies its API)
function async_call(method, ...args) {
  return new Promise((resolve, reject) => {
    method(...args, callback_generator(resolve, reject));
  });
}

const filter = web3.eth.filter("latest");
filter.watch((error, last_hash) => {
  async_call(web3.eth.getBlock, last_hash).then((block) => {
    return block.number;
  }).then(update_state);
});

function update_state(block_number) {
  return get_crowdsale_state(block_number)
  .then((state) => {
    cached_state = state;
    // cached_page = original_page.replace("_sold_tokens_", state.sold_tokens) 
    //   .replace("_investor_count_", state.investor_count) 
    //   .replace("_finalized_", state.finalized) 
    //   .replace("_starting_timestamp_", state.starting_timestamp) 
    //   .replace("_ending_timestamp_", state.ending_timestamp) 
    //   .replace("_minimum_buy_", state.minimum_buy);
  });
}

async_call(web3.eth.getBlock, "latest").then((block) => update_state(block.number));

async function init_async(object, prop_key, promise) {
  object[prop_key] = await promise;
}

// Eventually we may want to bind calls to a certain block number. (TODO)
async function get_crowdsale_state(block_number) {
  // We return the amount raised, number of investors,
  // progress of the current phase and current phase number.
  const state = { "current_block": block_number };
  const promises = [];

  promises.push(init_async(state, "sold_tokens", async_call(crowdsale.tokensSold.call, block_number).then((sold) => { return web3.fromWei(sold);})));
  promises.push(init_async(state, "investor_count", async_call(crowdsale.investorCount.call, block_number)));
  promises.push(init_async(state, "finalized", async_call(crowdsale.finalized.call, block_number)));
  promises.push(init_async(state, "starting_timestamp", async_call(crowdsale.startsAt.call, block_number)));
  promises.push(init_async(state, "ending_timestamp", async_call(crowdsale.endsAt.call, block_number)));
  promises.push(init_async(state, "minimum_buy", async_call(crowdsale.minimum_buy_value.call, block_number).then((minimum) => { return web3.fromWei(minimum)})));
  
  console.log(promises);
  await Promise.all(promises).catch((error) => console.log("Promise failed: " + error));
  return state;
}




module.exports = { get_crowdsale_state, crowdsale };