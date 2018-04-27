#!/usr/bin/env python3

from util.deployer import Deployer
from util.web3_interface import Web3Interface
from util.tx_checker import fails, succeeds

web3 = Web3Interface().w3
web3.miner.start(1)
deployer = Deployer()
owner = web3.eth.accounts[0]
new_owner = web3.eth.accounts[1]
gas = 5000000
gas_price = 20000000000
tx = {"from": owner, "value": 0, "gas": gas, "gasPrice": gas_price}
(ownable_contract, tx_hash) = deployer.deploy("./build/ownable/", "Ownable", owner, tx,)
receipt = web3.eth.waitForTransactionReceipt(tx_hash)
assert receipt.status == 1
functions = ownable_contract.functions

def owner():
  functions.owner().call()

assert owner() == owner
succeeds("Transfer ownership succeeds.", functions.transferOwnership(new_owner).transact(tx))
assert owner() == new_owner
web3.miner.stop()