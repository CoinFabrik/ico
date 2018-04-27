#!/usr/bin/env python3

from util.deployer import Deployer
from util.web3_interface import Web3Interface
from util.tx_checker import fails, succeeds
from util.test_config2 import config_f

web3 = Web3Interface().w3
web3.miner.start(1)
deployer = Deployer()
accounts = web3.eth.accounts
sender = accounts[0]
gas = 50000000
gas_price = 20000000000
tx = {"from": sender, "value": 0, "gas": gas, "gasPrice": gas_price}
config = config_f()

(mintable_token_contract, tx_hash) = deployer.deploy("./build/", "MintableTokenMock", tx['from'], tx, config['multisig_supply'], config['MW_address'], True)
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
  return functions.mint(receiver, amount).transact(tx_args)

print("Test fails: - mint with wrong mint agent")
print("            - mint with wrong mint agent and can't mint")
print("            - mint with can't mint")
print("            - setMintAgent with wrong owner")
print("            - setMintAgent with wrong owner and can't mint")
print("            - setMintAgent with can't mint")
print("            - multisig == 0x0")
print("            - mintable false and initialSupply == 0, correct multisig")

print("Test success: - mint")
print("              - setMintAgent")

tx['from'] = accounts[2]
fails("setMintAgent with account 1 and account 2 as sender: fails because it's the wrong owner", set_mint_agent(accounts[1], True, tx))

tx['from'] = accounts[1]
fails("mint to account 2 and account 1 as sender: fails because it's the wrong mint agent", mint(accounts[2], True, tx))