#!/usr/bin/env python3

from util.deployer import Deployer
from util.web3_interface import Web3Interface
from util.tx_checker import fails, succeeds

web3 = Web3Interface().w3
web3.miner.start(1)
owner = web3.eth.accounts[0]
new_owner = web3.eth.accounts[1]
tx = {'from': owner, 'gas': 100000000, 'gasPrice': 20000000000}
deployer = Deployer()
(haltable_contract, tx_hash) = deployer.deploy("./build/haltable/", "Haltable", owner, tx,)
receipt = web3.eth.waitForTransactionReceipt(tx_hash)
assert receipt.status == 1
assert haltable_contract.functions.halted().call() == False
succeeds("Halt succeeds", haltable_contract.functions.halt().transact(tx))
assert haltable_contract.functions.halted().call() == True
succeeds("Unhalt succeeds", haltable_contract.functions.unhalt().transact(tx))
assert haltable_contract.functions.halted().call() == False
assert haltable_contract.functions.owner().call() == owner
succeeds("Transfer ownership succeeds.", haltable_contract.functions.transferOwnership(new_owner).transact(tx))
assert haltable_contract.functions.owner().call() == new_owner
web3.miner.stop()