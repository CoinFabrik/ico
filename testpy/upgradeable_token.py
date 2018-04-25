#!/usr/bin/env python3

from util.deployer import Deployer
from util.web3_interface import Web3Interface
from util.tx_checker import fails, succeeds

web3 = Web3Interface().w3
web3.miner.start(1)
deployer = Deployer()
sender = master = web3.eth.accounts[0]
new_master = web3.eth.accounts[1]
gas = 50000000
gas_price = 20000000000
tx = {"from": sender, "value": 0, "gas": gas, "gasPrice": gas_price}
original_supply = 525 * (10 ** 3) * (10 ** 18)

(upgrade_agent_contract, tx_hash2) = deployer.deploy("./build/upgrade_agent/", "UpgradeAgentMock", sender, tx, original_supply)
receipt2 = web3.eth.waitForTransactionReceipt(tx_hash2)
assert receipt2.status == 1
(upgradeable_token_contract, tx_hash) = deployer.deploy("./build/upgradeable_token/", "UpgradeableTokenMock", master, tx, original_supply)
receipt = web3.eth.waitForTransactionReceipt(tx_hash)
assert receipt.status == 1

assert upgradeable_token_contract.functions.canUpgrade().call()
print(upgrade_agent_contract.address)
succeeds("setUpgradeAgent succeeds", upgradeable_token_contract.functions.setUpgradeAgent(upgrade_agent_contract.address).transact(tx))
#fails("setUpgradeAgent fails", upgradeable_token_contract.functions.setUpgradeAgent(upgrade_agent_contract.address).transact(tx))

succeeds("upgrade succeeds", upgradeable_token_contract.functions.upgrade(12345678910).transact(tx))
#fails("upgrade fails", upgradeable_token_contract.functions.upgrade(12345678910).transact(tx))

assert upgradeable_token_contract.functions.getUpgradeState().call() == 4

succeeds("changeUpgradeMaster succeeds", upgradeable_token_contract.functions.changeUpgradeMaster(new_master).transact(tx))
fails("changeUpgradeMaster fails", upgradeable_token_contract.functions.changeUpgradeMaster(new_master).transact(tx))

assert upgradeable_token_contract.functions.canUpgrade().call()

succeeds("setCanUp succeeds", upgradeable_token_contract.functions.setCanUp(False).transact(tx))

assert not upgradeable_token_contract.functions.canUpgrade().call()