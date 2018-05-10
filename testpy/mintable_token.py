#!/usr/bin/env python3

import sys
sys.path.append("../deployment")
from deployer import Deployer
from web3_interface import Web3Interface
from tx_checker import fails, succeeds
from test_config import config_f

web3 = Web3Interface().w3
web3.miner.start(1)
deployer = Deployer()
accounts = web3.eth.accounts
sender = accounts[0]
gas = 50000000
gas_price = 20000000000
tx = {"from": sender, "value": 0, "gas": gas, "gasPrice": gas_price}
config = config_f()
to_mint = 100000
address_zero = web3.toChecksumAddress("0x0000000000000000000000000000000000000000")

(mintable_token_contract, tx_hash) = deployer.deploy("./build/", "MintableTokenMock", tx, config['multisig_supply'], address_zero, True)
receipt = web3.eth.waitForTransactionReceipt(tx_hash)
assert receipt.status == 0


(mintable_token_contract, tx_hash) = deployer.deploy("./build/", "MintableTokenMock", tx, 0, config['MW_address'], False)
receipt = web3.eth.waitForTransactionReceipt(tx_hash)
assert receipt.status == 0


(mintable_token_contract, tx_hash) = deployer.deploy("./build/", "MintableTokenMock", tx, config['multisig_supply'], config['MW_address'], True)
receipt = web3.eth.waitForTransactionReceipt(tx_hash)
assert receipt.status == 1
functions = mintable_token_contract.functions


def get_minting_finished():
  return functions.mintingFinished().call()
def get_mint_agent(address):
  return functions.mintAgents(address).call()
def mint(receiver, amount, tx_args):
  return functions.mint(receiver, amount).transact(tx_args)
def set_mint_agent(address, state, tx_args):
  return functions.setMintAgent(address, state).transact(tx_args)

tx['from'] = accounts[1]
fails("setMintAgent with account 1 and account 1 as sender: fails because it's the wrong owner", set_mint_agent(accounts[1], True, tx))

tx['from'] = accounts[0]
succeeds("setMintAgent with account 1 and account 0 as sender: succeeds because it's the right owner", set_mint_agent(accounts[1], True, tx))

fails("mint to account 2 and account 0 as sender: fails because it's the wrong mint agent", mint(accounts[2], to_mint, tx))

tx['from'] = accounts[1]
succeeds("mint to account 2 and account 1 as sender: succeeds because it's the right mint agent", mint(accounts[2], to_mint, tx))


tx['from'] = accounts[0]
(mintable_token_contract, tx_hash) = deployer.deploy("./build/", "MintableTokenMock", tx, config['multisig_supply'], config['MW_address'], False)
receipt = web3.eth.waitForTransactionReceipt(tx_hash)
assert receipt.status == 1
functions = mintable_token_contract.functions

tx['from'] = accounts[1]
fails("setMintAgent with account 1 and account 1 as sender: fails because it's the wrong owner and can't mint", set_mint_agent(accounts[1], True, tx))

tx['from'] = accounts[0]
fails("setMintAgent with account 1 and account 0 as sender: fails because it can't mint", set_mint_agent(accounts[1], True, tx))

fails("mint to account 2 and account 0 as sender: fails because it's the wrong mint agent and can't mint", mint(accounts[2], to_mint, tx))

