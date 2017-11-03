const abi = require("./contracts_abi.js");
const config = require("./config.js");
const Web3 = require("web3");
const express = require("express");
const cors = require("cors");
const app = express();

const web3 = new Web3(new Web3.providers.HttpProvider(config.nodeIpPort));
const average_block_time = 21;

// Setup contract object
const CS_contract = web3.eth.contract(abi.Crowdsale);
const crowdsale = CS_contract.at(config.crowdsale.address);
// const ceiling_contract = web3.eth.contract(abi.FixedCeiling);

app.use(cors());
// app.options("*", cors());
app.use(express.static("../web_test"));

// Defined to avoid waiting on database or blockchain node to respond
app.head("/", function (request, response) {
    response.status(200);
    response.type("json");
});

app.get("/", function (request, response) {
    if (request.query.method != "query_crowdsale") {
        response.status(200);
        response.json({"error": "Method requested is not supported."});
        return;
    }
    get_crowdsale_state(web3.eth.blockNumber).then(function(state) {
        response.status(200);
        response.json(state);
    });
});

app.listen(8080);

const callback_generator = function (resolve, reject) {
    return function (error, value) {
        if (error) {
            reject(error);
        } else {
            resolve(value);
        }
    };
};

// Promisify a web3 asynchronous call (this becomes unnecessary as soon as web3 promisifies its API)
function async_call(method, ...args) {
    return new Promise(function (resolve, reject) {
        method(...args, callback_generator(resolve, reject));
    });
}

async function init_async(object, prop_key, promise) {
    object[prop_key] = await promise;
}

// Eventually we may want to bind calls to a certain block number. (TODO)
async function get_crowdsale_state(block_number) {
    // We return the amount raised, number of investors,
    const state = { "current_block": block_number };
    const promises = [];

    //TODO: bind calls for block number _block_
    promises.push(init_async(state, "ether_raised", async_call(crowdsale.weiRaised.call, block_number)));
    promises.push(init_async(state, "investor_count", async_call(crowdsale.investorCount.call, block_number)));
    promises.push(init_async(state, "finalized", async_call(crowdsale.finalized.call, block_number)));
    promises.push(init_async(state, "starting_timestamp", async_call(crowdsale.startsAt.call, block_number)));
    promises.push(init_async(state, "ending_timestamp", async_call(crowdsale.endsAt.call, block_number)));
    promises.push(init_async(state, "minimum_buy", async_call(crowdsale.minimum_buy_value.call, block_number)));

    console.log(promises);
    await Promise.all(promises).catch(function(error) {console.log("Promise failed: " + error);});

    // Convert Wei values into ether values.
    state.ether_raised = web3.fromWei(state.ether_raised);
    state.minimum_buy = web3.fromWei(state.minimum_buy);
    return state;
}


module.exports = { get_crowdsale_state, crowdsale };