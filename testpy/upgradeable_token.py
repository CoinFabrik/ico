#!/usr/bin/env python3

from util.deployer import Deployer
from util.web3_interface import Web3Interface
from util.tx_checker import fails, succeeds

web3 = Web3Interface().w3
web3.miner.start(1)
deployer = Deployer()
sender = master = web3.eth.accounts[0]
newmaster = web3.eth.accounts[1]
address_zero = "0x0000000000000000000000000000000000000000"
gas = 50000000
gas_price = 20000000000
tx0 = {"from": address_zero, "value": 0, "gas": gas, "gasPrice": gas_price}
txmaster = {"from": master, "value": 0, "gas": gas, "gasPrice": gas_price}
txmasterwogas = {"from": master, "value": 0}
txnewmaster = {"from": newmaster, "value": 0, "gas": gas, "gasPrice": gas_price}
original_supply = 525 * (10 ** 3) * (10 ** 18)

(upgrade_agent_contract, tx_hash_agent) = deployer.deploy("./build/", "UpgradeAgentMock", master, txmaster, original_supply)
receipt_agent = web3.eth.waitForTransactionReceipt(tx_hash_agent)
assert receipt_agent.status == 1
print("Deployed UpgradeAgentMock")
(upgradeable_token_contract, tx_hash) = deployer.deploy("./build/", "UpgradeableTokenMock", master, txmaster, original_supply)
receipt = web3.eth.waitForTransactionReceipt(tx_hash)
assert receipt.status == 1
print("Deployed UpgradeableTokenMock")
functions = upgradeable_token_contract.functions

print("Testing changeUpgradeMaster")
fails("changeUpgradeMaster fails calling with wrong master sender", functions.changeUpgradeMaster(newmaster).transact(txnewmaster))
assert functions.upgradeMaster().call() == master
fails("changeUpgradeMaster fails setting address_zero and correct master sender", functions.changeUpgradeMaster(address_zero).transact(txmaster))
assert functions.upgradeMaster().call() == master
succeeds("changeUpgradeMaster succeeds with correct master sender and setting new master", functions.changeUpgradeMaster(newmaster).transact(txmaster))
assert functions.upgradeMaster().call() == newmaster
succeeds("changeUpgradeMaster succeeds with correct master sender and setting old master", functions.changeUpgradeMaster(master).transact(txnewmaster))
assert functions.upgradeMaster().call() == master

assert functions.canUpgrade().call()
succeeds("setCanUp to False succeeds", functions.setCanUp(False).transact(txmaster))
assert not functions.canUpgrade().call()
assert functions.getUpgradeState().call()
fails("setUpgradeAgent fails with wrong master", functions.setUpgradeAgent(upgrade_agent_contract.address).transact(txnewmaster))
assert functions.upgradeAgent().call() == address_zero
fails("setUpgradeAgent fails setting address zero", functions.setUpgradeAgent(address_zero).transact(txmaster))
assert functions.upgradeAgent().call() == address_zero
fails("setUpgradeAgent fails with canUpgrade False", functions.setUpgradeAgent(upgrade_agent_contract.address).transact(txmaster))
assert functions.upgradeAgent().call() == address_zero
fails("upgrade fails with canUpgrade False (state NotAllowed)", functions.upgrade(10000000000).transact(txmaster))
assert functions.totalUpgraded().call() == 0

succeeds("setCanUp to True succeeds", functions.setCanUp(True).transact(txmaster))
assert functions.canUpgrade().call()
assert functions.getUpgradeState().call() == 2
fails("upgrade fails in state WaitingForAgent", functions.upgrade(10000000000).transact(txmaster))
assert functions.totalUpgraded().call() == 0
fails("setUpgradeAgent fails with wrong master", functions.setUpgradeAgent(upgrade_agent_contract.address).transact(txnewmaster))
assert functions.upgradeAgent().call() == address_zero
fails("setUpgradeAgent fails setting address zero", functions.setUpgradeAgent(address_zero).transact(txmaster))
assert functions.upgradeAgent().call() == address_zero
assert functions.upgradeMaster().call() == master
assert functions.canUpgrade().call()
assert upgrade_agent_contract.address != address_zero
assert functions.getUpgradeState().call() != 4
succeeds("setUpgradeAgent succeeds with canUpgrade True", functions.setUpgradeAgent(upgrade_agent_contract.address).transact(txmaster))
assert functions.upgradeAgent().call() == upgrade_agent_contract.address
assert functions.getUpgradeState().call() == 3
fails("upgrade fails sending value 0", functions.upgrade(0).transact(txmaster))
assert functions.totalUpgraded().call() == 0
succeeds("upgrade succeeds", functions.upgrade(10000000000).transact(txmaster))
assert functions.totalUpgraded().call() == 10000000000
assert functions.getUpgradeState().call() == 4

web3.miner.stop()