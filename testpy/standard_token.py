#!/usr/bin/env python3

from util.deployer import Deployer
from util.web3_interface import Web3Interface
from util.tx_checker import fails, succeeds
from util.estimate_gas import estimate_gas

web3 = Web3Interface().w3
web3.miner.start(1)
deployer = Deployer()
sender = web3.eth.accounts[0]
gas = 50000000
gas_price = 20000000000
tx = {"from": sender, "value": 0, "gas": gas, "gasPrice": gas_price}
tx_wo_gas = {"from": sender, "value": 0}

(standard_token_contract, tx_hash) = deployer.deploy("./build/", "StandardToken", sender, tx,)
receipt = web3.eth.waitForTransactionReceipt(tx_hash)
assert receipt.status == 1
print("Gas Used:", receipt.gasUsed)

