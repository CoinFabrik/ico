const abi = require("./contracts_abi.js");
const config = require("./config.js");
const Web3 = require("web3");
const express = require("express");
const app = express();
const Url = require("url");

const web3 = new Web3(new Web3.providers.HttpProvider(config.nodeIpPort));

// Setup contract objects
const CS_contract = web3.eth.contract(abi.Crowdsale);
const crowdsale = CS_contract.at(config.crowdsale.address);
const ceiling_contract = web3.eth.contract(abi.FixedCeiling);

app.use(express.static("../web_test"));

// Defined to avoid waiting on database or blockchain node to respond
app.head("/", function (request, response) {
    response.status(200);
    response.type("json");
});

app.listen(8080);

const callbackGenerator = function (resolve, reject) {
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
        method(...args, callbackGenerator(resolve, reject));
    });
}

async function init_async(object, prop_key, promise) {
    object[prop_key] = await promise;
}

// Eventually we may want to bind calls to a certain block number. (TODO)
async function get_crowdsale_state(block) {
    // We return the amount raised, number of investors,
    // progress of the current phase and current phase number.
    const state = {};
    const promises = [];

    //TODO: bind calls for block number _block_
    promises.push(init_async(state, "wei_raised", async_call(crowdsale.weiRaised.call)));
    promises.push(init_async(state, "investor_count", async_call(crowdsale.investorCount.call)));
    promises.push(init_async(state, "crowdsale_finalized", async_call(crowdsale.finalized.call)));
    
    // Separate case
    promises.push(async_call(crowdsale.ceilingStrategy.call).then(async function(ceiling_address) {
        const fixed_ceiling = ceiling_contract.at(ceiling_address);
        state.chunked_wei_multiple = await async_call(fixed_ceiling.chunkedWeiMultiple.call);
    }));
    console.log(promises);
    await Promise.all(promises).catch(function(error) {console.log("Promise failed: " + error);});

    state.current_phase = (state.wei_raised / state.chunked_wei_multiple + 1) | 0;
    state.phase_progress = state.wei_raised % state.chunked_wei_multiple;
    return state;
}




module.exports = { get_crowdsale_state, crowdsale };