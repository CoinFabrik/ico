#!/usr/bin/env python3

from web3_interface import Web3Interface, args
from contract import Contract
from tx_dump import dump
from tx_args import tx_args
if args.test:
  from test_config import config_f
else:
  from client_config import config_f

config = config_f()
c = [config['MW_address'], config['start_time'], config['end_time'], config['token_retriever_account'], config['tranches'], config['multisig_supply'], config['crowdsale_supply'], config['token_decimals'], config['max_tokens_to_sell']]

web3 = Web3Interface().w3
if web3.net.version == "1":
  sender_account = "0x54d9249C776C56520A62faeCB87A00E105E8c9Dc"
else:
  sender_account = web3.eth.accounts[0]

compiled_path = "./build/"
contract_name = "Crowdsale"
contract = Contract().load_contract(compiled_path, contract_name)
tx_args_dict = tx_args(sender_account, gas=2000000)
dump(web3, args, config, tx_args_dict)
configuration_tx_hash = contract.functions.configurationCrowdsale(*c).transact(tx_args_dict)
print("Configuration transaction hash: ", configuration_tx_hash.hex())