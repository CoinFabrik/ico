#!/usr/bin/env python3

import time
from web3_interface import Web3Interface
import json
import glob
import os
from load_contract import ContractLoader

class Crowdsale:

  gas = 5000000
  gas_price = 20000000000
  params = None
    
  # web3.py instance
  web3 = Web3Interface("middleware").w3
  miner = web3.miner
  accounts = web3.eth.accounts
  sender_account = accounts[0]
  contract = None
  tokens_to_preallocate = 10
  wei_price_of_preallocation = 350
  states = {"Unknown": 0, "PendingConfiguration": 1, "PreFunding": 2, "Funding": 3, "Success": 4, "Finalized": 5}
  
  def __init__(self, config_params):
    self.params = config_params
    loader = ContractLoader()
    self.contract = loader.load("./build/", "Crowdsale", address_path="./address_log/")

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

  def eta_ico(self):
    return round(self.starts_at()-time.time())

  def eta_end_ico(self):
    return round(self.ends_at()-time.time())

  def start_ico(self):
    print("ETA for ICO: " + str(self.eta_ico() + 1) + " seconds.")
    time.sleep(max(0, self.eta_ico() + 1))
    print("ICO STARTS")

  def end_ico(self):
    tokens_sold = self.tokens_sold()
    sellable_tokens = self.sellable_tokens()
    if tokens_sold >= sellable_tokens:
      print("ICO ENDS")
    else:
      print("ETA for ICO's end: " + str(self.eta_end_ico() + 1) + " seconds.")
      time.sleep(max(0, self.eta_end_ico() + 1))
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
    param_list = [self.params['MW_address'], self.params['startTime'], self.params['endTime'], self.params['token_retriever_account'], self.params['tranches'], self.params['multisig_supply'], self.params['crowdsale_supply'], self.params['token_decimals'], self.params['max_tokens_to_sell']]
    return self.get_transaction_receipt(self.contract.functions.configurationCrowdsale(*param_list).transact({"from": self.sender_account, "value": 0, "gas": self.gas, "gasPrice": self.gas_price}))

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
  
  def get_current_price(self):
    return self.get_transaction_receipt(self.contract.functions.getCurrentPrice(self.tokens_sold()).transact(self.transaction_info(self.sender_account)))

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
  
  def initial_bounties_tokens(self):
    return self.contract.functions.initial_tokens().call()

  def invested_amount_of(self):
    return self.contract.functions.investedAmountOf().call()
  
  def investor_count(self):
    return self.contract.functions.investorCount().call()
  
  def milieurs_per_eth(self):
    return self.contract.functions.milieurs_per_eth().call()

  def multisig_wallet(self):
    return self.contract.functions.multisigWallet().call()
  
  def minimum_buy_value(self):
    return self.contract.functions.minimum_buy_value().call()

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
  
  def set_ending_time(self, endingTime):
    return self.get_transaction_receipt(self.contract.functions.setEndingTime(endingTime).transact(self.transaction_info(self.sender_account)))

  def set_minimum_buy_value(self, new_minimum):
    return self.get_transaction_receipt(self.contract.functions.setMinimumBuyValue(new_minimum).transact(self.transaction_info(self.sender_account)))

  def set_require_customer_id(self, value):
    return self.get_transaction_receipt(self.contract.functions.setRequireCustomerId(value).transact(self.transaction_info(self.sender_account)))
  
  def set_require_signed_address(self, value, signer):
    return self.get_transaction_receipt(self.contract.functions.setRequireSignedAddress(value, signer).transact(self.transaction_info(self.sender_account)))
  
  def set_starting_time(self, startingTime):
    return self.get_transaction_receipt(self.contract.functions.setStartingTime(startingTime).transact(self.transaction_info(self.sender_account)))

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

  def update_eurs_per_eth(self, milieurs_amount):
    return self.get_transaction_receipt(self.contract.functions.updateEursPerEth(milieurs_amount).transact(self.transaction_info(self.sender_account)))
  
  def update_price_agent(self, new_price_agent):
    return self.get_transaction_receipt(self.contract.functions.updatePriceAgent(new_price_agent).transact(self.transaction_info(self.sender_account)))

  def wei_raised(self):
    return self.contract.functions.weiRaised().call()

