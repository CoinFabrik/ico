#!/usr/bin/env python3

import sys
sys.path.append("../deployment")
from deployer import Deployer
from web3_interface import Web3Interface
from tx_checker import fails, succeeds
import time

web3 = Web3Interface().w3
web3.miner.start(1)
deployer = Deployer()
accounts = web3.eth.accounts
sender = accounts[0]
gas = 50000000
gas_price = 20000000000
tx = {"from": sender, "value": 0, "gas": gas, "gasPrice": gas_price}
agent_to_approve = accounts[2]
tokens_to_approve = 100000

(standard_token_mock_contract, tx_hash_standard_token) = deployer.deploy("./build/", "StandardTokenMock", tx,)

time.sleep(1.4)

(lost_and_found_token_contract, tx_hash) = deployer.deploy("./build/", "LostAndFoundTokenMock", tx,)
receipt = web3.eth.waitForTransactionReceipt(tx_hash)
assert receipt.status == 1
functions = lost_and_found_token_contract.functions


def get_master():
  return functions.master().call()
def enable_lost_and_found(agent, tokens, token_contract, tx_args):
  return functions.enableLostAndFound(agent, tokens, token_contract).transact(tx_args)

assert get_master() == sender

tx['from'] = accounts[1]
fails("enableLostAndFound with account 1 as sender: fails because it's the wrong master", enable_lost_and_found(agent_to_approve, tokens_to_approve, standard_token_mock_contract.address, tx))

tx['from'] = accounts[0]
succeeds("enableLostAndFound with account 0 as sender: succeeds because it's the right master", enable_lost_and_found(agent_to_approve, tokens_to_approve, standard_token_mock_contract.address, tx))