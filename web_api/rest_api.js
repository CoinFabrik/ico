// const abi = require("./contracts_abi.js");
const config = require("./config.js");
const Web3 = require("web3");
const express = require("express");
const app = express();

const web3 = new Web3(new Web3.providers.HttpProvider(config.nodeIpPort));

// Setup contract objects
// const CS_contract = web3.eth.contract(abi.Crowdsale);
// const crowdsale = CS_contract.at(config.crowdsale.address);
// const ceiling_contract = web3.eth.contract(abi.FixedCeiling);

const CS_contract = web3.eth.contract(require("../build/contracts/HubiiCrowdsale.json").abi);
const crowdsale = CS_contract.at(config.crowdsale.address);
const ceiling_contract = web3.eth.contract(require("../build/contracts/FixedCeiling.json").abi);

app.use(express.static("../web_test"));

// Defined to avoid waiting on database or blockchain node to respond
app.head("/", function (request, response) {
    response.status(200);
    response.type("json");
});

app.get("/", function (request, response) {
    if (request.query.method != "query_crowdsale") {
        response.status(200);
        response.json({"error": "Method " + request.query.method.toString() + " requested is not supported."});
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
    // progress of the current phase and current phase number.
    const state = { "current_block": block_number };
    const promises = [];

    //TODO: bind calls for block number _block_
    promises.push(init_async(state, "wei_raised", async_call(crowdsale.weiRaised.call, block_number)));
    promises.push(init_async(state, "investor_count", async_call(crowdsale.investorCount.call, block_number)));
    promises.push(init_async(state, "crowdsale_finalized", async_call(crowdsale.finalized.call, block_number)));
    promises.push(init_async(state, "starting_block", async_call(crowdsale.startsAt.call, block_number)));
    promises.push(init_async(state, "ending_block", async_call(crowdsale.endsAt.call, block_number)));
    promises.push(init_async(state, "crowdsale_cap", async_call(crowdsale.weiFundingCap.call, block_number)));

    
    // Separate case
    promises.push(async_call(crowdsale.ceilingStrategy.call, block_number).then(async function(ceiling_address) {
        const fixed_ceiling = ceiling_contract.at(ceiling_address);
        state.wei_per_phase = await async_call(fixed_ceiling.chunkedWeiMultiple.call, block_number);
    }));
    console.log(promises);
    await Promise.all(promises).catch(function(error) {console.log("Promise failed: " + error);});

    state.current_phase = (state.wei_raised / state.wei_per_phase + 1) | 0;
    state.phase_progress = state.wei_raised % state.wei_per_phase;
    return state;
}




module.exports = { get_crowdsale_state, crowdsale };