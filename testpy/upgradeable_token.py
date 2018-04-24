#!/usr/bin/env python3

from util.deployer import Deployer
from util.web3_interface import Web3Interface
from util.tx_checker import fails, succeeds

web3 = Web3Interface().w3
web3.miner.start(1)
deployer = Deployer()
owner = web3.eth.accounts[0]
gas = 50000000
gas_price = 20000000000
tx = {"from": owner, "value": 0, "gas": gas, "gasPrice": gas_price}

(upgradeable_token_contract, tx_hash) = deployer.deploy("./build/upgradeable_token/", "UpgradeableTokenMock", owner, tx,)
web3.eth.waitForTransactionReceipt(tx_hash)