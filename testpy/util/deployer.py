from .web3_interface import Web3Interface
import json
from .address import generate_contract_address
from .load_contract import ContractLoader

class Deployer:
  web3 = None

  def __init__(self):
    self.web3 = Web3Interface().w3

  def deploy(self, path, contract_name, tx_args, *args):
    (contract_abi, contract_bytecode) = ContractLoader.get_abi_and_bytecode(path, contract_name)
    deployer_nonce = self.web3.eth.getTransactionCount(tx_args["from"])
    contract_address = generate_contract_address(tx_args["from"], deployer_nonce)
    contract = self.web3.eth.contract(address=contract_address, abi=contract_abi, bytecode=contract_bytecode)
    tx_hash = contract.constructor(*args).transact(transaction=tx_args)
    return (contract, tx_hash)