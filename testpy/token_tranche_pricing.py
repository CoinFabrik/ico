#!/usr/bin/env python3

import sys
sys.path.append("../deployment")
from deployer import Deployer
from web3_interface import Web3Interface
from tx_checker import fails, succeeds
from test_config2 import config_f

web3 = Web3Interface().w3
web3.miner.start(1)
deployer = Deployer()
owner = web3.eth.accounts[0]
gas = 50000000
gas_price = 20000000000
tx = {"from": owner, "value": 0, "gas": gas, "gasPrice": gas_price}
config = config_f()
tokens_sold_example = 37287 * 10 ** 20

(token_tranche_pricing_contract, tx_hash) = deployer.deploy("./build/", "TokenTranchePricingMock", tx,)
receipt = web3.eth.waitForTransactionReceipt(tx_hash)
assert receipt.status == 1
functions = token_tranche_pricing_contract.functions

def get_tranches_length():
  return functions.getTranchesLength().call()

print(get_tranches_length())
assert get_tranches_length() == 0
succeeds("Configuration of TokenTranchePricing succeeds.", functions.configurateTokenTranchePricingMock(config['tranches']).transact(tx))
print(get_tranches_length())
assert get_tranches_length() == 5
assert functions.getCurrentPriceMock(tokens_sold_example).call() == 20000000000000000000
web3.miner.stop()