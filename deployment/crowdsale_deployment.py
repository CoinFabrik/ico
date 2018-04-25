#!/usr/bin/env python3

from web3_interface import Web3Interface
import json
import unlocker
import os, errno
from datetime import datetime
from deployer import Deployer
import sys
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--network", default="poanet")
parser.add_argument("-p", "--provider", default="http")
parser.add_argument("-t", "--test", action="store_true")
parser.add_argument("-c", "--configurate", action="store_true")
args = parser.parse_args()

# web3.py instance
web3 = Web3Interface().w3
miner = web3.miner
if web3.net.chainId == 1:
  sender_account = "0x54d9249C776C56520A62faeCB87A00E105E8c9Dc"
else:
  sender_account = web3.eth.accounts[0]
gas = 5000000
address_log_path = "./address_log/"
compiled_path = "./build/"
crowdsale_contract = None
tx_hash = None

if args.test:
  unlocker.unlock()
  miner.start(1)
  contract_name = "Crowdsale"
  gas_price = 20000000000
else:
  contract_name = input("\nEnter contract's name: ")
  gas_price = input("\nEnter gas price: ")

def deploy():
  deployer = Deployer()
  print("\nDeploying contract...")
  (crowdsale_contract, tx_hash) = deployer.deploy(compiled_path, contract_name, {"from": sender_account, "value": 0, "gas": gas, "gasPrice": gas_price},)
  print("\nDeployment transaction hash: ", tx_hash.hex(),
        "\nCrowdsale address: ", crowdsale_contract.address)
  write_to_address_log(crowdsale_contract)

def write_to_address_log(contract):
  # Write json file with contract's address into address_log folder
  if args.test:
    deployment_name = "test"
  else:
    deployment_name = input("Enter a name for the deployment: ") 
 
  local_time = datetime.now()
  json_file_name = "Contract-Address" + '--' + local_time.strftime('%Y-%m-%d--%H-%M-%S') + '--' + deployment_name
  
  try:
    if not os.path.exists(address_log_path):
      os.makedirs(address_log_path)
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise
  
  file_path_name_w_ext = address_log_path + json_file_name + '.json'
  address_for_file = {'contract_address': contract.address}
  with open(file_path_name_w_ext, 'w') as fp:
    json.dump(address_for_file, fp, sort_keys=True, indent=2)

if __name__ == '__main__':
  deploy()
  if args.configurate:
    import configurate
    configurate.configurate()