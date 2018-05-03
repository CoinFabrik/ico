#!/usr/bin/env python3

import sys
sys.path.append("../deployment")
from deployer import Deployer
from web3_interface import Web3Interface
from tx_checker import fails, succeeds
from test_config import config_f
from crowdsale_checker import CrowdsaleChecker

web3 = Web3Interface().w3
config = config_f()
crowdsale_interface = CrowdsaleChecker(config)
web3.miner.start(1)
deployer = Deployer()
accounts = web3.eth.accounts
sender = accounts[0]
gas = 50000000
gas_price = 20000000000
tx = {"from": sender, "value": 0, "gas": gas, "gasPrice": gas_price}

(generic_crowdsale_contract, tx_hash) = deployer.deploy("./build/", "GenericCrowdsaleMock", tx,)
receipt = web3.eth.waitForTransactionReceipt(tx_hash)
assert receipt.status == 1
functions = generic_crowdsale_contract.functions

