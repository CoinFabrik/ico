#!/usr/bin/env python3

import time
from web3 import Web3, IPCProvider, HTTPProvider
from web3.middleware import geth_poa_middleware
import json
import glob
import os

class Crowdsale:

  gas = 50000000
  gas_price = 20000000000
  params = None
  
  # Change ipcPath if needed
  ipc_path = '/home/coinfabrik/Programming/blockchain/node/geth.ipc'
  # web3.py instance
  web3 = Web3(IPCProvider(ipc_path))
  web3.middleware_stack.inject(geth_poa_middleware, layer=0)
  print(web3.version.node)
  # web3 = Web3(HTTPProvider("http://localhost:8545"))
  miner = web3.miner
  accounts = web3.eth.accounts
  sender_account = accounts[0]
  contract = None
  tokens_to_preallocate = 10
  wei_price_of_preallocation = 350
  states = {"Unknown": 0, "PendingConfiguration": 1, "PreFunding": 2, "Funding": 3, "Success": 4, "Finalized": 5}
  
  def __init__(self, config_params):
    self.params = config_params
    # Get Crowdsale ABI
    with open("./build/Crowdsale.abi") as contract_abi_file:
      crowdsale_abi = json.load(contract_abi_file)
    
    # Get Crowdsale Bytecode
    with open("./build/Crowdsale.bin") as contract_bin_file:
      crowdsale_bytecode = '0x' + contract_bin_file.read()
    
    file_list = glob.glob('./address_log/*')
    latest_file = max(file_list, key=os.path.getctime)
    # Get Syndicatev2 address
    with open(latest_file) as contract_address_file:
      crowdsale_address_json = json.load(contract_address_file)

    crowdsale_address = crowdsale_address_json['crowdsale_address']

    # Crowdsale instance creation
    self.contract = self.web3.eth.contract(address=crowdsale_address, abi=crowdsale_abi, bytecode=crowdsale_bytecode)

  # Custom functions-------------------------------------------------------------------------
  def get_transaction_receipt(self, tx_hash):
    self.wait(tx_hash)
    return self.web3.eth.getTransactionReceipt(tx_hash)

  # Transaction parameter
  def transaction_info(self, sender, value=0):
    return {"from": sender, "value": value*(10**18), "gas": self.gas, "gasPrice": self.gas_price}

  def wait(self, tx_hash):
    while self.web3.eth.getTransactionReceipt(tx_hash) == None:
      time.sleep(1)

  def send_ether_to_crowdsale(self, buyer, value):
    return self.get_transaction_receipt(self.web3.eth.sendTransaction({'from': buyer, 'to': self.contract.address, 'value': value, 'gas': 100000000}))

  def eta_ico():
    return round(self.starts_at()-time.time())

  def eta_end_ico():
    return round(self.ends_at()-time.time())

  def start_ico(self):
    print("ETA for ICO: " + str(self.eta_ico()) + " seconds.")
    time.sleep(max(0, self.eta_ico()))
    print("ICO STARTS")

  def end_ico(self):
    tokens_sold = self.tokens_sold()
    sellable_tokens = self.sellable_tokens()
    if tokens_sold >= sellable_tokens:
      print("ICO ENDS")
    else:
      print("ETA for ICO's end: " + str(self.eta_end_ico()) + " seconds.")
      time.sleep(max(0, self.eta_end_ico()))
      print("ICO ENDS")


  # Crowdsale Contract's functions-----------------------------------------------------------
  def buy(self, buyer, value):
    return self.get_transaction_receipt(self.contract.functions.buy().transact(self.transaction_info(buyer, value)))

  def buy_on_behalf(self, buyer, receiver, value):
    return self.get_transaction_receipt(self.contract.functions.buyOnBehalf(receiver).transact(self.transaction_info(buyer, value)))
  
  def buy_on_behalf_with_customer_id(self, buyer, receiver, customerId, value):
    return self.get_transaction_receipt(self.contract.functions.buyOnBehalfWithCustomerId(receiver, customerId).transact(self.transaction_info(buyer, value)))
  
  def buy_on_behalf_with_signed_address(self, buyer, receiver, customerId, v, r, s, value):
    return self.get_transaction_receipt(self.contract.functions.buyOnBehalfWithSignedAddress(receiver, customerId, v, r, s).transact(self.transaction_info(buyer, value)))
  
  def buy_with_customer_id(self, customerId, buyer, value):
    return self.get_transaction_receipt(self.contract.functions.buyWithCustomerId(customerId).transact(self.transaction_info(buyer, value)))
  
  def buy_with_signed_address(self, customerId, v, r, s, buyer, value):
    return self.get_transaction_receipt(self.contract.functions.buyWithSignedAddress(customerId, v, r, s).transact(self.transaction_info(buyer, value)))
  
  def configuration_crowdsale(self):
    return self.get_transaction_receipt(self.contract.functions.configurationCrowdsale(self.params[0], self.params[1], self.params[2], self.params[3], self.params[4], self.params[5], self.params[6], self.params[7], self.params[8]).transact({"from": self.sender_account, "value": 0, "gas": self.gas, "gasPrice": self.gas_price}))

  def configured(self):
    return self.contract.functions.configured().call()
  
  def early_participant_whitelist(self, address):
    return self.contract.functions.earlyParticipantWhitelist(address).call()
  
  def ends_at(self):
    return self.contract.functions.endsAt().call()
  
  def finalize(self):
    return self.get_transaction_receipt(self.contract.functions.finalize().transact(self.transaction_info(self.sender_account)))
  
  def finalized(self):
    return self.contract.functions.finalized().call()
  
  def get_deployment_block(self):
    return self.contract.functions.getDeploymentBlock().call()
  
  def get_state(self):
    return self.contract.functions.getState().call()
  
  def get_tranches_length(self):
    return self.contract.functions.getTranchesLength().call()
  
  def halt(self):
    return self.get_transaction_receipt(self.contract.functions.halt().transact(self.transaction_info(self.sender_account)))
  
  def halted(self):
    return self.contract.functions.halted().call()
  
  def invested_amount_of(self):
    return self.contract.functions.investedAmountOf().call()
  
  def investor_count(self):
    return self.contract.functions.investorCount().call()
  
  def multisig_wallet(self):
    return self.contract.functions.multisigWallet().call()
  
  def owner(self):
    return self.contract.functions.owner().call()
  
  def preallocate(self, receiver, fullTokens, weiPrice):
    return self.get_transaction_receipt(self.contract.functions.preallocate(receiver, fullTokens, weiPrice).transact(self.transaction_info(self.sender_account)))
  
  def require_customer_id(self):
    return self.contract.functions.requireCustomerId().call()
  
  def required_signed_address(self):
    return self.contract.functions.requiredSignedAddress().call()
  
  def sellable_tokens(self):
    return self.contract.functions.sellable_tokens().call()

  def set_early_participant_whitelist(self, addr, status):
    return self.get_transaction_receipt(self.contract.functions.setEarlyParticipantWhitelist(addr, status).transact(self.transaction_info(self.sender_account)))
  
  def set_require_customer_id(self, value):
    return self.get_transaction_receipt(self.contract.functions.setRequireCustomerId(value).transact(self.transaction_info(self.sender_account)))
  
  def set_require_signed_address(self, value, signer):
    return self.get_transaction_receipt(self.contract.functions.setRequireSignedAddress(value, signer).transact(self.transaction_info(self.sender_account)))
  
  def signer_address(self):
    return self.contract.functions.signerAddress().call()
  
  def starts_at(self):
    return self.contract.functions.startsAt().call()
  
  def token(self):
    return self.contract.functions.token().call()
  
  def token_amount_of(self):
    return self.contract.functions.tokenAmountOf().call()
  
  def tokens_sold(self):
    return self.contract.functions.tokensSold().call()
  
  def tranches(self):
    return self.contract.functions.tranches().call()
  
  def transfer_ownership(self, newOwner):
    return self.get_transaction_receipt(self.contract.functions.transferOwnership(newOwner).transact(self.transaction_info(self.sender_account)))
  
  def unhalt(self):
    return self.get_transaction_receipt(self.contract.functions.unhalt().transact(self.transaction_info(self.sender_account)))
  
  def wei_raised(self):
    return self.contract.functions.weiRaised().call()

