#!/usr/bin/env python3

import sys
from datetime import datetime
import json
import time
import os, errno
import unlocker
from web3_interface import Web3Interface
from load_contract import ContractLoader
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--network", default="poanet", help="Enter network, defaults to poanet")
parser.add_argument("-p", "--provider", default="http", help="Enter provider, defaults to http")
parser.add_argument("-a", "--address", help="Enter address to look for log file")
parser.add_argument("-d", "--deployment_name", help="Enter deployment name to look for log file")
parser.add_argument("-t", "--test", action="store_true", help="Testing mode")
parser.add_argument("-c", "--configurate", action="store_true")
args = parser.parse_args()

if args.test:
  from test_config import config_f
else:
  from client_config import config_f
config = config_f()
c = [config['MW_address'], config['startTime'], config['endTime'], config['token_retriever_account'], config['tranches'], config['multisig_supply'], config['crowdsale_supply'], config['token_decimals']]

web3 = Web3Interface().w3
miner = web3.miner
if web3.net.version == "1":
  sender_account = "0x54d9249C776C56520A62faeCB87A00E105E8c9Dc"
else:
  sender_account = web3.eth.accounts[0]
gas = 2100000
gas_price = None
log_path = "./log/"

loader = ContractLoader()
contract = loader.load("./build/", "Crowdsale", log_path=log_path)

# Display configuration parameters, confirm them, write them to json file
def dump():  
  # Displaying configuration parameters ----------------------------------------------------------------------------------
  print("\nWeb3 version:", web3.version.api)
  print("\nWeb3 network:", args.network)
  print(
    "\n\nMultisig address:", config['MW_address'], 
    "\n\nStart time:", time.asctime(time.gmtime(config['startTime'])) + " (GMT)",
    "\n\nEnd time:", time.asctime(time.gmtime(config['endTime'])) + " (GMT)",
    "\n\nToken retriever: " + config['token_retriever_account']
  );  
  for x in range(int((len(config['tranches'])/4))):
    print("\nTranche #", x, " -----------------------------------------------------------------",
      "\nFullTokens cap:", int(config['tranches'][4*x]/(10**18)),
      "\nStart:         ", time.asctime(time.gmtime(config['tranches'][4*x+1])) + " (GMT)",
      "\nEnd:           ", time.asctime(time.gmtime(config['tranches'][4*x+2])) + " (GMT)",
      "\nTokens per EUR:", config['tranches'][4*x+3]
    )  
  print("------------------------------------------------------------------------------");
  print("\nTransaction sender: " + sender_account,
        "\nGas and Gas price: " + str(gas) + " and " + str(gas_price) + "\n"
  )  
  # ----------------------------------------------------------------------------------------------------------------------
  # Validating configuration parameters
  pending_input = True
  consent = None
  while pending_input:
    consent = input('\nDo you agree with the information? [yes/no]: ')
    if consent == 'yes':
      pending_input = False
    elif consent == 'no':
      sys.exit("Aborted")
    else:
      print("\nPlease enter 'yes' or 'no'\n")
  
  ContractLoader.exists_folder(log_path)
  
  # Writing configuration parameters into json file for logging purposes
  (log_json, file_path) = ContractLoader.get_deployment_json_and_path(log_path, deployment_name=args.deployment_name, address=args.address)
  log_json.update(config)
  with open(file_path, 'w') as fp:
    json.dump(log_json, fp, sort_keys=True, indent=2)

def configurate(contract=None, address=None, abi=None, bytecode=None):
  if address and abi and bytecode:
    contract = web3.eth.contract(address=address, abi=abi, bytecode=bytecode)
  configuration_tx_hash = contract.functions.configurationCrowdsale(*c).transact({"from": sender_account, "value": 0, "gas": gas, "gasPrice": gas_price})
  print("Configuration transaction hash: ", configuration_tx_hash.hex())
  return configuration_tx_hash

if __name__ == '__main__':
  if args.test:
    unlocker.unlock()
    miner.start(1)
    gas_price = 5000000000
  else:
    gas_price = 10100000000 #input("Enter gas price: ")
    dump()
  configurate(contract=contract)