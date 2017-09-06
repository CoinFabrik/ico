const abi = require("./contracts_abi.js");
const config = require("./config.js");
const net = require("net");
const Web3 = require("web3");
const express = require("express");
const cors = require("cors");
const app = express();

const web3 = new Web3(new Web3.providers.IpcProvider(config.ipc_file, net));
const average_block_time = 25;

// Setup contract objects
const CS_contract = web3.eth.contract(abi.Crowdsale);
const crowdsale = CS_contract.at(config.crowdsale.address);
const ceiling_contract = web3.eth.contract(abi.FixedCeiling);
const fixed_ceiling = ceiling_contract.at(config.ceiling_strategy.address);

// local cache
let last_block_queried;
let cached_state;

const cors_options = { origin: [ "https://hubii.network", "https://www.hubii.network" ] };
app.use(cors(cors_options));
// app.options("*", cors());
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
  const state = { "current_block": block_number, "average_block_time": average_block_time };
  const promises = [];

  promises.push(init_async(state, "ether_raised", async_call(crowdsale.weiRaised.call, block_number).then((wei_raised) => {
    return web3.fromWei(wei_raised);
  })));
  promises.push(init_async(state, "investor_count", async_call(crowdsale.investorCount.call, block_number)));
  promises.push(init_async(state, "finalized", async_call(crowdsale.finalized.call, block_number)));
  promises.push(init_async(state, "starting_block", async_call(crowdsale.startsAt.call, block_number)));
  promises.push(init_async(state, "ending_block", async_call(crowdsale.endsAt.call, block_number)));
  promises.push(init_async(state, "cap", async_call(crowdsale.weiFundingCap.call, block_number).then((cap) => {
    return web3.fromWei(cap);
  })));
  promises.push(init_async(state, "minimum_goal", async_call(crowdsale.minimumFundingGoal.call, block_number).then((minimum_goal) => {
    return web3.fromWei(minimum_goal);
  })));
  promises.push(init_async(state, "ether_per_phase", async_call(fixed_ceiling.chunkedWeiMultiple.call, block_number).then((ether_per_phase) => {
    return web3.fromWei(ether_per_phase);
  })));
  // console.log(promises);
  await Promise.all(promises).catch((error) => console.log("Promise failed: " + error));

  // state.start_timestamp_utc = (new Date()).getTime() + (state.starting_block - state.current_block) * average_block_time * 1000;
  // state.end_timestamp_utc = (new Date()).getTime()  + (state.ending_block - state.current_block) * average_block_time * 1000;
  // state.start_eta = new Date(state.start_timestamp_utc).toISOString().replace(/T/, ' ').replace(/\..+/, '');
  // state.end_eta = new Date(state.end_timestamp_utc).toISOString().replace(/T/, ' ').replace(/\..+/, '');
  state.current_phase = (state.ether_raised / state.ether_per_phase + 1) | 0;
  state.phase_progress = web3.fromWei(state.ether_raised % state.ether_per_phase);
  return state;
}




module.exports = { get_crowdsale_state, crowdsale };