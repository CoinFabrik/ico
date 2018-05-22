import glob
import os
from web3_interface import Web3Interface, args
import json
import rlp
from eth_utils import keccak, to_checksum_address


class Contract:

  web3 = None
  args = None

  def __init__(self):
    self.web3 = Web3Interface().w3
    self.args = args

  def instantiate_contract(self, sender_address, compiled_path, contract_name):
    (contract_abi, contract_bytecode) = self.get_abi_and_bytecode(compiled_path, contract_name)
    sender_nonce = self.web3.eth.getTransactionCount(sender_address)
    contract_address = self.generate_contract_address(sender_address, sender_nonce)
    contract = self.web3.eth.contract(address=contract_address, abi=contract_abi, bytecode=contract_bytecode)
    return contract
  
  def load_address(self, log_path):
    if self.args.address:
      return self.args.address
    elif self.args.deployment_name:
      log_json, _ = self.get_deployment_json_and_path(log_path, self.args.deployment_name, self.args.address)
      address = log_json["contract_address"]
      return address
  
  def load_contract(self, compiled_path, contract_name, log_path="./log/"):
    (contract_abi, contract_bytecode) = self.get_abi_and_bytecode(compiled_path, contract_name)
    contract_address = self.load_address(log_path)
    contract = self.web3.eth.contract(address=contract_address, abi=contract_abi, bytecode=contract_bytecode)
    return contract
  
  def deploy(self, path, contract_name, tx_args, *args):
    contract = self.instantiate_contract(tx_args["from"], path, contract_name)
    tx_hash = contract.constructor(*args).transact(transaction=tx_args)
    return (contract, tx_hash)

  @staticmethod  
  def generate_contract_address(address, nonce):
    return to_checksum_address('0x' + keccak(rlp.encode([bytes(bytearray.fromhex(address[2:])), nonce]))[-20:].hex())
  
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
      substring = deployment_name + "-"
    elif address:
      substring = address
    file_list = glob.glob(path + '*')
    filtered_file_list = filter(lambda x : substring in x, file_list)
    latest_file_path = max(filtered_file_list, key=os.path.getctime)
    with open(latest_file_path) as log_file:
      log_json = json.load(log_file)
    return (log_json, latest_file_path)