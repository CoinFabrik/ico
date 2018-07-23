#!/usr/bin/env python3

from web3_interface import Web3Interface
import json
from datetime import datetime
from contract import Contract
from log import log_address
from tx_args import tx_args

web3 = Web3Interface().w3
if web3.net.version == "1":
  sender_account = "0x54d9249C776C56520A62faeCB87A00E105E8c9Dc"
else:
  sender_account = web3.eth.accounts[0]
compiled_path = "./build/"
contract_name = "Crowdsale"
contract = Contract()
print("\nDeploying contract...")
tx_hash = contract.deploy(compiled_path, contract_name, tx_args(sender_account, gas=4500000),)
print("\nDeployment transaction hash: ", tx_hash.hex(),
      "\nCrowdsale address: ", contract.contract.address)
log_address(contract.contract)