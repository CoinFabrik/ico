#!/usr/bin/env python3

import sys
sys.path.append("../deployment")
from deployer import Deployer
from web3_interface import Web3Interface
from tx_checker import fails, succeeds
from test_config import config_f

web3 = Web3Interface().w3
config = config_f()
web3.miner.start(1)
deployer = Deployer()
accounts = web3.eth.accounts
sender = accounts[0]
gas = 50000000
gas_price = 20000000000
tx = {"from": sender, "value": 0, "gas": gas, "gasPrice": gas_price}

(crowdsale_token_contract, tx_hash) = deployer.deploy("./build/", "CrowdsaleToken", tx, config["multisig_supply"], config["token_decimals"], config["MW_address"], config["token_retriever_account"])
receipt = web3.eth.waitForTransactionReceipt(tx_hash)
assert receipt.status == 1
functions = crowdsale_token_contract.functions

def can_upgrade():
  return functions.canUpgrade().call()
def release_token_transfer(tx_args):
  return functions.releaseTokenTransfer().transact(tx_args)

assert functions.name().call() == "BurgerKoenig"
assert functions.symbol().call() == "BK"
assert functions.decimals().call() == config["token_decimals"]
assert functions.lost_and_found_master().call() == config["token_retriever_account"]
assert not can_upgrade()
fails("releaseTokenTransfer fails because sender isn't the releaseAgent.", release_token_transfer(tx))
succeeds("setReleaseAgent succeeds because the sender is the owner.", functions.setReleaseAgent(accounts[1]).transact(tx))
tx["from"] = accounts[1]
succeeds("releaseTokenTransfer succeeds because sender is the releaseAgent.", release_token_transfer(tx))
assert can_upgrade()