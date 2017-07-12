const abi = require("./contracts_abi.js");
const config = require("./config.js");
const Web3 = require("web3");

const web3 = new Web3(new Web3.providers.HttpProvider(config.nodeIpPort));

// Setup contract objects
const CS_contract = web3.eth.contract(abi.Crowdsale);
const crowdsale = CS_contract.at(config.crowdsale.address);
const ceiling_contract = web3.eth.contract(abi.FixedCeiling);


const callbackGenerator = function (resolve, reject) {
    return function (error, value) {
        if (error) {
            reject(error);
        } else {
            resolve(value);
        }
    };
};

function async_call(method, ...args) {
    return new Promise(function (resolve, reject) {
        method(...args, callbackGenerator(resolve, reject));
    });
}

async function init_async(object, prop_key, promise) {
    object[prop_key] = await promise;
}

// Eventually we may want to bind calls to a certain block number. (TODO 1)
async function get_crowdsale_state(block) {
    // We return the amount raised, number of investors,
    // progress of the current phase and current phase number.
    let state = {};
    let promises = [];

    //TODO 1: bind calls for block number _block_
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



// testing only
let id_time = 0;
let increased_time = 0;

function test_buy(amount) {
    function increaseTime(delta_seconds) {
        web3.currentProvider.send({ "jsonrpc": "2.0", method: "evm_increaseTime", "id": id_time, "params": [ delta_seconds ] });
        id_time++;
        increased_time += delta_seconds;
    }
    function currentTime() {
        return ((Date.now() / 1000) | 0) + increased_time;
    }
    web3.eth.defaultAccount = web3.eth.accounts[0];
    const timeDelta = 1500562800 - currentTime(); //!! cast expression to int with OR 0
    if (timeDelta > 0)
        increaseTime(timeDelta);
    return crowdsale.buy.sendTransaction({ value: web3.toWei(amount), gas: 300000, gas_price: 20000000000 });
}

module.exports = { get_crowdsale_state, crowdsale, test_buy };