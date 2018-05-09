import glob
import os
from web3_interface import Web3Interface
import json
import argparse

class ContractLoader:
  web3 = None
  args = None
  def __init__(self):
    self.web3 = Web3Interface().w3
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--network", default="poanet", help="Enter network, defaults to poanet")
    parser.add_argument("-p", "--provider", default="http", help="Enter provider, defaults to http")
    parser.add_argument("-t", "--test", action="store_true", help="Testing mode")
    parser.add_argument("-a", "--address", help="Enter address to look for log file")
    parser.add_argument("-d", "--deployment_name", help="Enter deployment name to look for log file")
    self.args = parser.parse_args()

def load(self, compiled_path, contract_name, log_path):
  (contract_abi, contract_bytecode) = self.get_abi_and_bytecode(compiled_path, contract_name)
  if self.args.address:
    contract = self.web3.eth.contract(address=self.args.address, abi=contract_abi, bytecode=contract_bytecode)
  try:
    if self.args.deployment_name:
      log_json = self.get_deployment_json(log_path, self.args.deployment_name, self.args.address)
      loaded_address = log_json["contract_address"]
      contract = self.web3.eth.contract(address=loaded_address, abi=contract_abi, bytecode=contract_bytecode)
  except FileNotFoundError:
    print("File not found")
  return contract
      
@staticmethod
def get_abi_and_bytecode(compiled_path, contract_name):
  with open(compiled_path + contract_name + ".abi") as contract_abi_file:
    contract_abi = json.load(contract_abi_file)
  with open(compiled_path + contract_name + ".bin") as contract_bin_file:
    contract_bytecode = '0x' + contract_bin_file.read()
  return (contract_abi, contract_bytecode)

@staticmethod
def exists_folder(path):
  try:
    if not os.path.exists(path):
      os.makedirs(path)
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise

@staticmethod
def get_deployment_json_and_path(path, deployment_name=None, address=None):
  substring = None
  if deployment_name:
    substring = deployment_name
  elif address:
    substring = address
  file_list = glob.glob(path + '*')
  filtered_file_list = filter(lambda x : substring in x, file_list)
  latest_file = max(filtered_file_list, key=os.path.getctime)
  with open(latest_file) as log_file:
    log_json = json.load(log_file)
  return (log_json, latest_file)