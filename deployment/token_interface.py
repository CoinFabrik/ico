#!/usr/bin/env python3

import time
from web3_interface import Web3Interface
import json

class Token:

  gas = 50000000
  gas_price = 20000000000
  params = None
  
  web3 = Web3Interface(middleware=True).w3
  miner = web3.miner
  accounts = web3.eth.accounts
  sender_account = accounts[0]
  owner = None

  def __init__(self, crowdsale_contract):
    self.owner = crowdsale_contract.address
    # Get CrowdsaleToken ABI
    with open("./build/CrowdsaleToken.abi") as token_abi_file:
      token_abi = json.load(token_abi_file)
    
    token_address = crowdsale_contract.functions.token().call()
    self.contract = self.web3.eth.contract(address=token_address, abi=token_abi)
  
  # Custom functions-------------------------------------------------------------------------
  def balances(self):
    for i in self.web3.eth.accounts:
      print(balance_of(i))

  def get_transaction_receipt(self, tx_hash):
    self.wait(tx_hash)
    return self.web3.eth.getTransactionReceipt(tx_hash)

  # Transaction parameter
  def transaction_info(self, sender, value=0):
    return {"from": sender, "value": value*(10**18), "gas": self.gas, "gasPrice": self.gas_price}

  def wait(self, tx_hash):
    while self.web3.eth.getTransactionReceipt(tx_hash) == None:
      time.sleep(1)

  # Token Contract's functions---------------------------------------------------------------
  def add_approval(self, spender, addedValue):
    return self.contract.functions.addApproval(spender, addedValue).transact(self.transaction_info(self.sender_account))
  
  def allowance(self, account, spender):
    return self.contract.functions.allowance(account, spender).call()
  
  def approve(self, spender, value):
    return self.contract.functions.approve(spender, value).transact(self.transaction_info(self.sender_account))
  
  def balance_of(self, investor):
    if isinstance(investor, str):
      return self.contract.functions.balanceOf(investor).call()
    else:
      return self.contract.functions.balanceOf(self.web3.eth.accounts[investor]).call()
  
  def can_upgrade(self):
    return self.contract.functions.canUpgrade().call()
  
  def change_upgrade_master(self, newMaster):
    return self.contract.functions.changeUpgradeMaster(newMaster).transact(self.transaction_info(self.sender_account))
  
  def decimals(self):
    return self.contract.functions.decimals().call()
  
  def enable_lost_and_found(self, agent, tokens, token_contr):
    return self.contract.functions.enableLostAndFound(agent, tokens, token_contr).transact(self.transaction_info(self.sender_account))
  
  def get_upgrade_state(self):
    return self.contract.functions.getUpgradeState().call()
  
  def set_transfer_agent(self, addr, state):
    return self.get_transaction_receipt(self.contract.functions.setTransferAgent(addr, state).transact(self.transaction_info(self.owner)))

  def sub_approval(self, spender, subtractedValue):
    return self.contract.functions.subApproval(spender, subtractedValue).transact(self.transaction_info(self.sender_account))
  
  def total_supply(self):
    return self.contract.functions.totalSupply().call()
  
  def transfer_agents(self, agent):
    return self.contract.functions.transferAgents(agent).call()

  def transfer(self, to, value):
    return self.contract.functions.transfer(to, value).transact(self.transaction_info(self.sender_account))
  
  def transferFrom(self, from_addr, to, value):
    return self.contract.functions.transferFrom(from_addr, to, value).transact(self.transaction_info(self.sender_account))