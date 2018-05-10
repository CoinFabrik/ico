#!/usr/bin/env python3

import sys
sys.path.append("../deployment")
from deployer import Deployer
from web3_interface import Web3Interface
from tx_checker import fails, succeeds

web3 = Web3Interface().w3
web3.miner.start(1)
owner = web3.eth.accounts[0]
new_owner = web3.eth.accounts[1]
tx = {'from': owner, 'gas': 100000000, 'gasPrice': 20000000000}
deployer = Deployer()
(haltable_contract, tx_hash) = deployer.deploy("./build/", "Haltable", tx,)
receipt = web3.eth.waitForTransactionReceipt(tx_hash)
assert receipt.status == 1
functions = haltable_contract.functions

def halted():
  return functions.halted().call()
def get_owner():
  return functions.owner().call()

assert halted() == False
succeeds("Halt succeeds", functions.halt().transact(tx))
assert halted() == True
succeeds("Unhalt succeeds", functions.unhalt().transact(tx))
assert halted() == False
assert get_owner() == owner
succeeds("Transfer ownership succeeds.", functions.transferOwnership(new_owner).transact(tx))
assert get_owner() == new_owner
web3.miner.stop()