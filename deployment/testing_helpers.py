#!/usr/bin/python3 -i

import time
from web3 import Web3, IPCProvider
import json

class Crowdsale:

  gas = 50000000
  gas_price = 20000000000
  params = None
  
  # Change ipcPath if needed
  ipc_path = '/home/coinfabrik/Programming/blockchain/node/geth.ipc'
  # web3.py instance
  web3 = Web3(IPCProvider(ipc_path))
  miner = web3.miner
  accounts = web3.eth.accounts
  sender_account = accounts[0]

  def __init__(self, crowdsale_address):
    # Get Crowdsale ABI
    with open("./build/Crowdsale.abi") as contract_abi_file:
      crowdsale_abi = json.load(contract_abi_file)
    
    # Get Crowdsale Bytecode
    with open("./build/Crowdsale.bin") as contract_bin_file:
      crowdsale_bytecode = '0x' + contract_bin_file.read()
    
    # Crowdsale instance creation

    self.contract = self.web3.eth.contract(address=crowdsale_address, abi=crowdsale_abi, bytecode=crowdsale_bytecode)

  # Custom functions-------------------------------------------------------------------------
  def get_transaction_receipt(self, tx_hash):
    status_deploy_crowdsale = status(tx_hash)
    if status_deploy_crowdsale == 1:
      return self.web3.eth.getTransactionReceipt(tx_hash)
  
  def status(self, tx_receipt):
    self.wait()
    return self.web3.eth.getTransactionReceipt(tx_receipt).status
  
  # Transaction parameter
  def transaction_info(self, sender, value=0):
    return {"from": sender, "value": value*(10**18), "gas": self.gas, "gasPrice": self.gas_price}

  def wait(self):
    block_number = self.web3.eth.blockNumber
    while self.web3.eth.blockNumber <= (block_number + 1):
      time.sleep(1)
  
  # Crowdsale Contract's functions-----------------------------------------------------------
  def buy(self, buyer, value):
    return self.status(self.contract.functions.buy().transact(self.transaction_info(buyer, value)))
  
  def buy_on_behalf(self, receiver, value):
    return status(self.contract.functions.buyOnBehalf(receiver).transact(transaction_info(self.sender_account, value)))
  
  def buy_on_behalf_with_customer_id(self, receiver, customerId, value):
    return status(self.contract.functions.buyOnBehalfWithCustomerId(receiver, customerId).transact(transaction_info(self.sender_account, value)))
  
  def buy_on_behalf_with_signed_address(self, receiver, customerId, v, r, s, value):
    return status(self.contract.functions.buyOnBehalfWithSignedAddress(receiver, customerId, v, r, s).transact(transaction_info(self.sender_account, value)))
  
  def buy_with_customer_id(self, customerId, value):
    return status(self.contract.functions.buyOnBehalfWithSignedAddress(customerId).transact(transaction_info(self.sender_account, value)))
  
  def buy_with_signed_address(self, customerId, v, r, s, value):
    return status(self.contract.functions.buyWithSignedAddress(customerId, v, r, s).transact(transaction_info(self.sender_account, value)))
  
  def configured(self):
    return self.contract.functions.configured().call()
  
  def early_participant_whitelist(self):
    return self.contract.functions.earlyParticipantWhitelist().call()
  
  def ends_at(self):
    return self.contract.functions.endsAt().call()
  
  def finalize(self):
    new_ending = int(time.time()) + 5
    print(status(self.contract.functions.setEndingTime(new_ending).transact(transaction_info(self.sender_account))))
    time.sleep(2)
    print(status(self.contract.functions.finalize().transact(transaction_info(self.sender_account))))
  
  def finalized(self):
    return self.contract.functions.finalized().call()
  
  def get_deployment_block(self):
    return self.contract.functions.getDeploymentBlock().call()
  
  def get_state(self):
    return self.contract.functions.getState().call()
  
  def get_tranches_length(self):
    return self.contract.functions.getTranchesLength().call()
  
  def halt(self):
    return status(self.contract.functions.halt().transact(transaction_info(self.sender_account)))
  
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
    return status(self.contract.functions.preallocate(receiver, fullTokens, weiPrice).transact(transaction_info(self.sender_account)))
  
  def require_customer_id(self):
    return self.contract.functions.requireCustomerId().call()
  
  def required_signed_address(self):
    return self.contract.functions.requiredSignedAddress().call()
  
  def set_early_participant_whitelist(self, addr, status):
    return status(self.contract.functions.setEarlyParticipantWhitelist(addr, status).transact(transaction_info(self.sender_account)))
  
  def set_require_customer_id(self, value):
    return status(self.contract.functions.setRequireCustomerId(value).transact(transaction_info(self.sender_account)))
  
  def set_require_signed_address(self, value, signer):
    return status(self.contract.functions.setRequireSignedAddress(value, signer).transact(transaction_info(self.sender_account)))
  
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
    return status(self.contract.functions.transferOwnership(newOwner).transact(transaction_info(self.sender_account)))
  
  def unhalt(self):
    return status(self.contract.functions.unhalt().transact(transaction_info(self.sender_account)))
  
  def wei_raised(self):
    return self.contract.functions.weiRaised().call()


class Token:

  gas = 50000000
  gas_price = 20000000000
  params = None
  
  # Change ipcPath if needed
  ipc_path = '/home/coinfabrik/Programming/blockchain/node/geth.ipc'
  # web3.py instance
  web3 = Web3(IPCProvider(ipc_path))
  miner = web3.miner
  accounts = web3.eth.accounts
  sender_account = accounts[0]

  def __init__(self, crowdsale_contract):
    # Get CrowdsaleToken ABI
    with open("./build/CrowdsaleToken.abi") as token_abi_file:
      token_abi = json.load(token_abi_file)
    
    token_address = crowdsale_contract.functions.token().call()
    self.contract = self.web3.eth.contract(address=token_address, abi=token_abi)
  
  # Custom functions-------------------------------------------------------------------------
  def balances(self):
    for i in self.web3.eth.accounts:
      print(balance_of(i))

  # Token Contract's functions---------------------------------------------------------------
  def add_approval(self, spender, addedValue):
    return self.contract.functions.addApproval(spender, addedValue).transact(transaction_info(self.sender_account))
  
  def allowance(self, account, spender):
    return self.contract.functions.allowance(account, spender).call()
  
  def approve(self, spender, value):
    return self.contract.functions.approve(spender, value).transact(transaction_info(self.sender_account))
  
  def balance_of(self, investor):
    if isinstance(investor, str):
      return self.contract.functions.balanceOf(investor).call()
    else:
      return self.contract.functions.balanceOf(self.web3.eth.accounts[investor]).call()
  
  def can_upgrade(self):
    return self.contract.functions.canUpgrade().call()
  
  def change_upgrade_master(self, newMaster):
    return self.contract.functions.changeUpgradeMaster(newMaster).transact(transaction_info(self.sender_account))
  
  def decimals(self):
    return self.contract.functions.decimals().call()
  
  def enable_lost_and_found(self, agent, tokens, token_contr):
    return self.contract.functions.enableLostAndFound(agent, tokens, token_contr).transact(transaction_info(self.sender_account))
  
  def get_upgrade_state(self):
    return self.contract.functions.getUpgradeState().call()
  
  def sub_approval(self, spender, subtractedValue):
    return self.contract.functions.subApproval(spender, subtractedValue).transact(transaction_info(self.sender_account))
  
  def total_supply(self):
    return self.contract.functions.totalSupply().call()
  
  def transfer(self, to, value):
    return self.contract.functions.transfer(to, value).transact(transaction_info(self.sender_account))
  
  def transferFrom(self, from_addr, to, value):
    return self.contract.functions.transferFrom(from_addr, to, value).transact(transaction_info(self.sender_account))  