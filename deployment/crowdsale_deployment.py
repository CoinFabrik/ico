#!/usr/bin/env python3

from web3_interface import Web3Interface
import json
import unlocker
import os, errno
from datetime import datetime
from deployer import Deployer
import sys
import argparse
from load_contract import ContractLoader

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--network", default="poanet", help="Enter network, defaults to poanet")
parser.add_argument("-p", "--provider", default="http", help="Enter provider, defaults to http")
parser.add_argument("-t", "--test", action="store_true", help="Testing mode")
parser.add_argument("-c", "--configurate", action="store_true")
args = parser.parse_args()

# web3.py instance
web3 = Web3Interface().w3
miner = web3.miner
if web3.net.version == "1":
  sender_account = "0x54d9249C776C56520A62faeCB87A00E105E8c9Dc"
else:
  sender_account = web3.eth.accounts[0]
gas = 4500000
log_path = "./log/"
compiled_path = "./build/"
tx_hash = None
contract_name = "Crowdsale"

if args.test:
  unlocker.unlock()
  miner.start(1)
  gas_price = 5000000000
else:
  #input("\nEnter contract's name: ")
  gas_price = 9100000000 #input("\nEnter gas price: ")

def deploy():
  deployer = Deployer()
  print("\nDeploying contract...")
  (contract, tx_hash) = deployer.deploy(compiled_path, contract_name, {"from": sender_account, "value": 0, "gas": gas, "gasPrice": gas_price},)
  print("\nDeployment transaction hash: ", tx_hash.hex(),
        "\nCrowdsale address: ", contract.address)
  write_to_address_log(contract)
  return contract

def write_to_address_log(contract):
  # Write json file with contract's address into address_log folder
  if args.test:
    deployment_name = "test"
  else:
    deployment_name = input("Enter a name for the deployment: ") 
 
  local_time = datetime.now()
  json_file_name = deployment_name + '--' + local_time.strftime('%Y-%m-%d--%H-%M-%S') + "--" + contract.address
  
  ContractLoader.exists_folder(log_path)
  
  file_path_name_w_ext = log_path + json_file_name + '.json'
  address_for_file = {'contract_address': contract.address}
  with open(file_path_name_w_ext, 'w') as fp:
    json.dump(address_for_file, fp, sort_keys=True, indent=2)

if __name__ == '__main__':
  crowdsale_contract = deploy()
  if args.configurate:
    import configurate
    configurate.configurate(address=crowdsale_contract.address, abi=crowdsale_contract.abi, bytecode=crowdsale_contract.bytecode)