#!/usr/bin/env python3

from util.deployer import Deployer
from util.web3_interface import Web3Interface
from util.tx_checker import fails, succeeds
from util.test_config2 import config_f

web3 = Web3Interface().w3
web3.miner.start(1)
deployer = Deployer()
owner = web3.eth.accounts[0]
gas = 50000000
gas_price = 20000000000
tx = {"from": owner, "value": 0, "gas": gas, "gasPrice": gas_price}
config = config_f()

(token_tranche_pricing_contract, tx_hash) = deployer.deploy("./build/token_tranche_pricing/", "TokenTranchePricingMock", owner, tx,)
receipt = web3.eth.waitForTransactionReceipt(tx_hash)
assert receipt.status == 1
print(token_tranche_pricing_contract.functions.getTranchesLength().call())
assert token_tranche_pricing_contract.functions.getTranchesLength().call() == 0
succeeds("Configuration of TokenTranchePricing succeeds.", token_tranche_pricing_contract.functions.configurateTokenTranchePricingMock(config['tranches']).transact(tx))
print(token_tranche_pricing_contract.functions.getTranchesLength().call())
assert token_tranche_pricing_contract.functions.getTranchesLength().call() == 5
print(token_tranche_pricing_contract.functions.getCurrentPriceMock(3728700000000000000000000).call())
assert token_tranche_pricing_contract.functions.getCurrentPriceMock(3728700000000000000000000).call() == 20000000000000000000
web3.miner.stop()