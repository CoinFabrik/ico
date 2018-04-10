#!/usr/bin/env python3

from util.deployer import Deployer
from util.web3_interface import Web3Interface
from util.tx_checker import fails, succeeds
from util.config import config_f


web3 = Web3Interface(middleware=True).w3

deployer = Deployer()

owner = web3.eth.accounts[0]
gas = 50000000
gas_price = 20000000000

config = config_f("testNet")

(token_tranche_pricing_contract, receipt) = deployer.deploy("./build/token_tranche_pricing/", "TokenTranchePricingMock", owner, {"from": owner, "value": 0, "gas": gas, "gasPrice": gas_price},)

assert token_tranche_pricing_contract.functions.getTranchesLength().call() == 0

assert token_tranche_pricing_contract.functions.getCurrentPriceMock(3500000).call() == 0

succeeds("Configuration of TokenTranchePricing succeeds.", token_tranche_pricing_contract.functions.configurateTokenTranchePricingMock(config['tranches']).transact({"from": owner, "value": 0, "gas": gas, "gasPrice": gas_price}))

assert token_tranche_pricing_contract.functions.getTranchesLength().call() == 2

assert token_tranche_pricing_contract.functions.getCurrentPriceMock(3500000).call() == 0