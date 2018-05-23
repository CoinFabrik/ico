#!/usr/bin/env python3

from web3_interface import Web3Interface, args
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
contract = Contract()
print("\nDeploying contract...")
(crowdsale_contract, tx_hash) = contract.deploy(compiled_path, "Crowdsale", tx_args(sender_account, gas=4500000),)
print("\nDeployment transaction hash: ", tx_hash.hex(),
      "\nCrowdsale address: ", crowdsale_contract.address)
log_address(crowdsale_contract)