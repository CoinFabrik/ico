#!/usr/bin/env python3

from util.deployer import Deployer
from util.web3_interface import Web3Interface
from util.tx_checker import fails, succeeds
from util.unlock import Unlocker

web3 = Web3Interface().w3
web3.miner.start(1)
unlocker = Unlocker()
unlocker.unlock()
deployer = Deployer()
owner = web3.eth.accounts[0]
new_owner = web3.eth.accounts[1]
gas = 5000000
gas_price = 20000000000
tx = {"from": owner, "value": 0, "gas": gas, "gasPrice": gas_price}

(ownable_contract, tx_hash) = deployer.deploy("./build/ownable/", "Ownable", owner, tx,)
web3.eth.waitForTransactionReceipt(tx_hash)
assert ownable_contract.functions.owner().call() == owner
succeeds("Transfer ownership succeeds.", ownable_contract.functions.transferOwnership(new_owner).transact(tx))
assert ownable_contract.functions.owner().call() == new_owner

web3.miner.stop()