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
from config import config_f

if __name__ == '__main__':
  config = config_f('liveNet')
else:
  config = config_f('testNet')
  unlocker = Unlock()
  unlocker.unlock()

web3 = Web3Interface(middleware=True).w3
miner = web3.miner
sender_account = web3.eth.accounts[0]
gas = 50000000
gas_price = 20000000000
params_log_path = "./params_log/"
params = [config['multisig_owners'], config['startTime'], config['endTime'], config['token_retriever_account'], config['tranches'], config['multisig_supply'], config['crowdsale_supply'], config['token_decimals'], config['max_tokens_to_sell']]

loader = ContractLoader()

contract = loader.load("./build/", "Crowdsale", address_path="./address_log/")

# Get CrowdsaleToken ABI
with open("./build/CrowdsaleToken.abi") as token_abi_file:
  token_abi = json.load(token_abi_file)

def wait(tx_hash):
  while web3.eth.getTransactionReceipt(tx_hash) == None:
    time.sleep(1)

# Display configuration parameters, confirm them, write them to json file
def dump():  
  pending_input = True
  consent = None
  
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

def configuration_details(web3, contract, tx_hash):
  if __name__ == '__main__':
    wait(tx_hash)
    receipt = web3.eth.getTransactionReceipt(tx_hash)
    print("\nConfiguration successful: " + str(receipt.status == 1))
    token_address = contract.functions.token().call()
    token_contract = web3.eth.contract(address=token_address, abi=token_abi)
    return token_contract

def configurate(f):
  config_tx_hash = contract.functions.configurationCrowdsale(*params).transact({"from": sender_account, "value": 0, "gas": gas, "gasPrice": gas_price})
  print("\nConfiguration Tx Hash: " + config_tx_hash.hex())
  return f(web3, contract, config_tx_hash)

if __name__ == '__main__':
  dump()
  configurate(configuration_details)