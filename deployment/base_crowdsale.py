#!/usr/bin/env python3

import time
from web3_interface import Web3Interface
import json
from load_contract import ContractLoader
from tx_args import gas, gasPrice, tx_args

class BaseCrowdsale:

  contract = None
  params = None
  sender_account = None
  web3 = None
  accounts = None
  states = None
  
  def __init__(self, log_path, config_params=None):
    self.web3 = Web3Interface().w3
    self.accounts = web3.eth.accounts
    if self.web3.version.network == "1":
      self.sender_account = "0x54d9249C776C56520A62faeCB87A00E105E8c9Dc"
    else:
      self.sender_account = self.accounts[0]
    self.params = config_params
    self.states = {"Unknown": 0, "PendingConfiguration": 1, "PreFunding": 2, "Funding": 3, "Success": 4, "Finalized": 5}
    loader = ContractLoader()
    self.contract = loader.load("./build/", "Crowdsale", log_path)

  def send_ether_to_crowdsale(self, buyer, value):
    return self.web3.eth.sendTransaction({'from': buyer, 'to': self.contract.address, 'value': value * (10 ** 18), 'gas': 100000000})

  def eta_ico(self):
    return round(self.starts_at()-time.time())

  def eta_end_ico(self):
    return round(self.ends_at()-time.time())

  def start_ico(self):
    print("ETA for ICO: " + str(self.eta_ico() + 2) + " seconds.")
    time.sleep(max(0, self.eta_ico() + 2))
    print("ICO STARTS")

  def end_ico(self):
    tokens_sold = self.tokens_sold()
    sellable_tokens = self.sellable_tokens()
    if tokens_sold >= sellable_tokens:
      print("ICO ENDS")
    else:
      print("ETA for ICO's end: " + str(self.eta_end_ico() + 2) + " seconds.")
      time.sleep(max(0, self.eta_end_ico() + 2))
      print("ICO ENDS")


  # Crowdsale Contract's functions-----------------------------------------------------------
  def buy(self, buyer, value):
    return self.contract.functions.buy().transact(self.transaction_info(buyer, value))

  def buy_on_behalf(self, buyer, receiver, value):
    return self.contract.functions.buyOnBehalf(receiver).transact(self.transaction_info(buyer, value))
  
  def buy_on_behalf_with_customer_id(self, buyer, receiver, customerId, value):
    return self.contract.functions.buyOnBehalfWithCustomerId(receiver, customerId).transact(self.transaction_info(buyer, value))
  
  def buy_on_behalf_with_signed_address(self, buyer, receiver, customerId, v, r, s, value):
    return self.contract.functions.buyOnBehalfWithSignedAddress(receiver, customerId, v, r, s).transact(self.transaction_info(buyer, value))
  
  def buy_with_customer_id(self, customerId, buyer, value):
    return self.contract.functions.buyWithCustomerId(customerId).transact(self.transaction_info(buyer, value))
  
  def buy_with_signed_address(self, customerId, v, r, s, buyer, value):
    return self.contract.functions.buyWithSignedAddress(customerId, v, r, s).transact(self.transaction_info(buyer, value))
  
  def configuration_crowdsale(self):
    param_list = [self.params['MW_address'], self.params['start_time'], self.params['end_time'], self.params['token_retriever_account'], self.params['tranches'], self.params['multisig_supply'], self.params['crowdsale_supply'], self.params['token_decimals'], self.params['max_tokens_to_sell']]
    return self.contract.functions.configurationCrowdsale(*param_list).transact({"from": self.sender_account, "value": 0, "gas": self.gas, "gasPrice": self.gas_price})

  def configured(self):
    return self.contract.functions.configured().call()
  
  def early_participant_whitelist(self, address):
    return self.contract.functions.earlyParticipantWhitelist(address).call()
  
  def ends_at(self):
    return self.contract.functions.endsAt().call()
  
  def finalize(self):
    return self.contract.functions.finalize().transact(self.transaction_info(self.sender_account))
  
  def finalized(self):
    return self.contract.functions.finalized().call()
  
  def get_current_price(self):
    return self.contract.functions.getCurrentPrice(self.tokens_sold()).call()

  def get_deployment_block(self):
    return self.contract.functions.getDeploymentBlock().call()
  
  def get_state(self):
    return self.contract.functions.getState().call()
  
  def get_tranches_length(self):
    return self.contract.functions.getTranchesLength().call()
  
  def halt(self):
    return self.contract.functions.halt().transact(self.transaction_info(self.sender_account))
  
  def halted(self):
    return self.contract.functions.halted().call()
  
  def invested_amount_of(self):
    return self.contract.functions.investedAmountOf().call()
  
  def investor_count(self):
    return self.contract.functions.investorCount().call()
  
  def multisig_wallet(self):
    return self.contract.functions.multisigWallet().call()
 
  def minimum_buy_value(self):
    return self.contract.functions.minimum_buy_value().call()
 
  def owner(self):
    return self.contract.functions.owner().call()
  
  def preallocate(self, receiver, fullTokens, weiPrice):
    receiver = self.web3.toChecksumAddress(receiver)
    return self.contract.functions.preallocate(receiver, fullTokens, weiPrice).transact(self.transaction_info(self.sender_account))
  
  def require_customer_id(self):
    return self.contract.functions.requireCustomerId().call()
  
  def required_signed_address(self):
    return self.contract.functions.requiredSignedAddress().call()
  
  def sellable_tokens(self):
    return self.contract.functions.sellable_tokens().call()

  def set_early_participant_whitelist(self, addr, status):
    return self.contract.functions.setEarlyParticipantWhitelist(addr, status).transact(self.transaction_info(self.sender_account))
 
  def set_starting_time(self, starting_time):
    return self.contract.functions.setStartingTime(starting_time).transact(self.transaction_info(self.sender_account))

  def set_ending_time(self, ending_time):
    return self.contract.functions.setEndingTime(ending_time).transact(self.transaction_info(self.sender_acount))
  
  def set_minimum_buy_value(self, new_minimum):
    return self.contract.functions.setMinimumBuyValue(new_minimum).transact(self.transaction_info(self.sender_account))
 
  def set_require_customer_id(self, value):
    return self.contract.functions.setRequireCustomerId(value).transact(self.transaction_info(self.sender_account))
  
  def set_require_signed_address(self, value, signer):
    return self.contract.functions.setRequireSignedAddress(value, signer).transact(self.transaction_info(self.sender_account))
  
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
    return self.contract.functions.transferOwnership(newOwner).transact(self.transaction_info(self.sender_account))
  
  def unhalt(self):
    return self.contract.functions.unhalt().transact(self.transaction_info(self.sender_account))
  
  def wei_raised(self):
    return self.contract.functions.weiRaised().call()