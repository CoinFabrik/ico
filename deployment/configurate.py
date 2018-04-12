#!/usr/bin/env python3

import sys
from datetime import datetime
import json
import time
import os, errno
import glob
from unlock import Unlock
from web3_interface import Web3Interface
from load_contract import ContractLoader
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--network", default="testnet")
parser.add_argument("-p", "--provider", default="http")
parser.add_argument("-t", "--test", action="store_true")
args = parser.parse_args()

if args.test:
  from test_config import config_f
else:
  from client_config import config_f

web3 = Web3Interface(middleware=True).w3
miner = web3.miner
sender_account = web3.eth.accounts[0]
gas = 5000000
gas_price = None
params_log_path = "./params_log/"
params = None

loader = ContractLoader()
contract = loader.load("./build/", "Crowdsale", address_path="./address_log/")

def wait(tx_hash):
  while web3.eth.getTransactionReceipt(tx_hash) == None:
    time.sleep(1)

# Display configuration parameters, confirm them, write them to json file
def dump():  
  # Displaying configuration parameters ----------------------------------------------------------------------------------
  print("\nWeb3 version:", web3.version.api)  
  print(
    "\n\nMultisig address:", config['multisig_owners'][0], 
    "\n\nStart time:", time.ctime(config['startTime']),
    "\n\nEnd time:", time.ctime(config['endTime']),
    "\n\nToken retriever: " + config['token_retriever_account']
  );  
  for x in range(0,int((len(config['tranches'])/4)-1)):
    print("\nTranche #", x, " -----------------------------------------------------------------",
      "\nFullTokens cap:", int(config['tranches'][4*x]/(10**18)),
      "\nStart:         ", time.ctime(config['tranches'][4*x+1]),
      "\nEnd:           ", time.ctime(config['tranches'][4*x+2]),
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
  deployment_name = input('\nEnter name of deployment: ')
  local_time = datetime.now()
  json_file_name = "Crowdsale" + '-' + local_time.strftime('%Y-%m-%d--%H-%M-%S') + '--' + deployment_name
  
  try:
    if not os.path.exists(params_log_path):
      os.makedirs(params_log_path)
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise
  
  # Writing configuration parameters into json file for logging purposes
  file_path_name_w_ext = params_log_path + json_file_name + '.json'
  with open(file_path_name_w_ext, 'w') as fp:
    json.dump(config, fp, sort_keys=True, indent=2)

def configurate(test):
  config_tx_hash = contract.functions.configurationCrowdsale(*c).transact({"from": sender_account, "value": 0, "gas": gas, "gasPrice": gas_price})
  if test:
    wait(config_tx_hash)
    receipt = web3.eth.getTransactionReceipt(config_tx_hash)
    print("\nConfiguration successful: " + str(receipt.status == 1))
    print("\nConfiguration Tx Hash: " + receipt.transactionHash.hex())
    print("\nGas used: " + str(receipt.gasUsed)  + "\n")
    return receipt
  else:
    return "\nConfiguration Tx Hash: " + config_tx_hash

if args.test:
  config = config_f()
  c = [config['MW_address'], config['startTime'], config['endTime'], config['token_retriever_account'], config['tranches'], config['multisig_supply'], config['crowdsale_supply'], config['token_decimals'], config['max_tokens_to_sell']]
  unlocker = Unlock()
  unlocker.unlock()
  miner.start(1)
  gas_price = 20000000000
  if __name__ == '__main__':
    configurate(args.test)
else:
  config = config_f()
  c = [config['MW_address'], config['startTime'], config['endTime'], config['token_retriever_account'], config['tranches'], config['multisig_supply'], config['crowdsale_supply'], config['token_decimals'], config['max_tokens_to_sell']]
  gas_price = input("Enter gas price: ")
  dump()
  configurate(args.test)