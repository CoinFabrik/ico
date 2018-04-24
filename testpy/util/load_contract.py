import glob
import os
from web3_interface import Web3Interface
import json

class ContractLoader:
  web3 = None

  def __init__(self):
    self.web3 = Web3Interface().w3

  def load(self, compiled_path, contract_name, address_path=None, contract_address=None):
    (contract_abi, contract_bytecode) = self.get_abi_and_bytecode(compiled_path, contract_name)
    if (contract_address == None) and (address_path != None):
      file_list = glob.glob(address_path + '*')
      latest_file = max(file_list, key=os.path.getctime)
      with open(latest_file) as contract_address_file:
        address_json = json.load(contract_address_file)
      contract_address = address_json[list(address_json.keys())[0]]
    contract = self.web3.eth.contract(address=contract_address, abi=contract_abi, bytecode=contract_bytecode)
    return contract

  def get_abi_and_bytecode(self, compiled_path, contract_name):
    with open(compiled_path + contract_name + ".abi") as contract_abi_file:
      contract_abi = json.load(contract_abi_file)
    with open(compiled_path + contract_name + ".bin") as contract_bin_file:
      contract_bytecode = '0x' + contract_bin_file.read()
    return (contract_abi, contract_bytecode)