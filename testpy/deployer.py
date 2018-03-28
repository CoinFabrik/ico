#!/usr/bin/env python3

from web3 import Web3, IPCProvider
import json
from address import generate_contract_address
from time import sleep

class Deployer:
  
  web3 = None

  def __init__(self, web3):
    self.web3 = web3

  def deploy(self, contract_name, tx_args, *args):
    with open("./build/" + contract_name + ".abi") as contract_abi_file:
      contract_abi = json.load(contract_abi_file)
    with open("./build/" + contract_name + ".bin") as contract_bin_file:
      contract_bytecode = '0x' + contract_bin_file.read()
    deployer_nonce = self.web3.eth.getTransactionCount(sender_account)
    contract_address = generate_contract_address(sender_account, deployer_nonce)
    contract = self.web3.eth.contract(address=contract_address, abi=contract_abi, bytecode=contract_bytecode)
    tx_hash = contract.deploy(transaction=tx_args, args=args)
    block_number = web3.eth.blockNumber
    while web3.eth.blockNumber <= (block_number + 1):
      sleep(1)
    assert web3.eth.getTransactionReceipt(tx_hash).status == 1
    return contract