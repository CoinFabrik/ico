from crowdsale_interface import Crowdsale
from investor import Investor
from tx_checker import fails, succeeds
import time
from load_contract import ContractLoader

class CrowdsaleChecker(Crowdsale):
  requiredCustomerId = False
  requiredSignedAddress = False
  halted = False
  state = None
  signer = None
  investors = []
  investment = 2
  start_time = None
  end_time = None
  multisig_wei = 0
  multisig_tokens = 0
  minimum_buy_value = None
  token_contract = None
  token_balances = None
  sold_tokens = 0
  tokens_to_preallocate = 10
  wei_price_of_preallocation = 350
  token_contract_name = None

  def __init__(self, params, contract_name, token_contract_name, addr_path=None, contract_addr=None):
    Crowdsale.__init__(self, params, contract_name, addr_path=addr_path, contract_addr=contract_addr)
    self.state = self.states["PendingConfiguration"]
    self.investors.append(Investor(self.accounts[1], True, 0))
    self.investors.append(Investor(self.accounts[2], True, 1))
    self.investors.append(Investor(self.accounts[3], False, 0))
    self.investors.append(Investor(self.accounts[4], False, 1))
    self.token_balances = {x : 0 for x in self.accounts}
    self.multisig_wei = self.web3.eth.getBalance(self.params['MW_address'])
    self.token_contract_name = token_contract_name
  
  def set_early_participant_whitelist(self):
    succeeds("Whitelist Account 1", super().set_early_participant_whitelist(self.accounts[1], True))
    succeeds("Whitelist Account 2", super().set_early_participant_whitelist(self.accounts[2], True))
  
  def require_customer_id(self):
    succeeds("Require Customer ID", self.set_require_customer_id(True))
    self.requiredCustomerId = True

  def unrequire_customer_id(self):
    succeeds("Unrequire Customer ID", self.set_require_customer_id(False))
    self.requiredCustomerId = False

  def require_signed_address(self, signer):
    succeeds("Require Signed Address", self.set_require_signed_address(True, signer))
    self.signer = signer
    self.requiredSignedAddress = True

  def require_signed_address(self, signer):
    succeeds("Unrequire Signed Address", self.set_require_signed_address(False, signer))
    self.signer = signer
    self.requiredSignedAddress = False

  def halt(self):
    succeeds("Halt Crowdsale", super().halt())
    self.halted = True

  def unhalt(self):
    succeeds("Unhalt Crowdsale", super().unhalt())
    self.halted = False
  
  def start_ico(self):
    super().start_ico()
    self.state = self.states["Funding"]
  
  def end_ico(self):
    super().end_ico()
    self.state = self.states["Success"]
 
  def check_state(self):
    assert self.get_state() == self.state

  def try_finalize(self):
    if self.state == self.states["Success"] and not self.halted:
      succeeds("Finalization of Crowdsale succeeds", self.finalize())
      self.state = self.states["Finalized"]
      self.check_all_end_balances()
    else:
      fails("Finalization of Crowdsale fails", self.finalize())
  
  def instantiate_token(self):
    loader = ContractLoader()
    contract = loader.load("./build/", self.token_contract_name, contract_address=self.token())
    return contract

  def check_all_end_balances(self):
    assert self.web3.eth.getBalance(self.multisig_wallet()) == self.multisig_wei
    assert self.token_balance(self.multisig_wallet()) == self.multisig_tokens
    assert self.crowdsale_balance() == 0
    for account in self.accounts:
      assert self.token_balance(account) == self.token_balances[account]

  def token_balance(self, address):
    return self.token_contract.functions.balanceOf(address).call()
  
  def crowdsale_balance(self):
    return self.web3.eth.getBalance(self.contract.address)

  def try_configuration_crowdsale(self):
    if self.state == self.states["PendingConfiguration"]:
      tx_hash = self.configuration_crowdsale()
      succeeds("Configuration of Crowdsale succeeds", tx_hash)
      tx_receipt = self.web3.eth.getTransactionReceipt(tx_hash)
      print("Configuration transaction used gas: ", tx_receipt.gasUsed,
             "\nConfiguration transaction hash: ", tx_hash.hex())
      self.state = self.states["PreFunding"]
      self.start_time = self.starts_at()
      self.end_time = self.ends_at()
      self.token_contract = self.instantiate_token()
      self.multisig_tokens = self.params['multisig_supply']
      assert self.token_balance(super().multisig_wallet()) == self.params['multisig_supply']
      assert self.token_balance(self.contract.address) == self.params['crowdsale_supply']
    else:
      fails("Configuration of Crowdsale fails", self.configuration_crowdsale())
    print("ETA for ICO: " + str(self.eta_ico() + 1) + " seconds.")
  
  def try_set_starting_time(self, starting_time):
    if self.state == self.states["PreFunding"] and int(round(time.time())) < starting_time and starting_time < self.ends_at():
      succeeds("Set starting time succeeds", self.set_starting_time(starting_time))
      self.start_time = starting_time
    else:
      fails("Set starting time fails", self.set_starting_time(starting_time))
   
  def try_set_ending_time(self, ending_time):
    if (self.state == self.states["PreFunding"] or self.state == self.states["Funding"]) and int(round(time.time())) < ending_time and self.starts_at() < ending_time:
      succeeds("Set starting time succeeds", self.set_ending_time(ending_time))
      self.end_time = ending_time
    else:
      fails("Set starting time fails", self.set_ending_time(ending_time))

  def try_set_minimum_buy_value(self, new_minimum):
    if (self.state == self.states["PreFunding"] or self.state == self.states["Funding"]):
      succeeds("Set minimum buy value succeeds", self.set_minimum_buy_value(new_minimum))
      self.minimum_buy_value = new_minimum
    else:
      fails("Set minimum buy value fails", self.set_minimum_buy_value(new_minimum))

  def calculate_token_amount(self, wei_amount, receiver):
    token_amount = None
    tokens_per_wei = self.get_current_price()
    max_allowed = (self.sellable_tokens() - self.tokens_sold()) // tokens_per_wei
    wei_allowed = min(max_allowed, wei_amount)
    if wei_amount < max_allowed:
      token_amount = tokens_per_wei * wei_amount
    else:
      token_amount = self.sellable_tokens() - self.tokens_sold()
    return (wei_allowed, token_amount)
 
  # Buy functions
  def try_preallocate(self):
    for investor in self.investors:
      tx_hash = self.preallocate(investor.address, self.tokens_to_preallocate, self.wei_price_of_preallocation)
      if self.state == self.states["PreFunding"] or self.state == self.states["Funding"]:
        succeeds("Preallocate succeeds", tx_hash)
        token_amount = self.tokens_to_preallocate * (10 ** 18)
        self.token_balances[investor.address] += token_amount
        print(investor.address)
        print(investor.whitelisted)
        print(self.token_balance(investor.address))
        print(self.token_balances[investor.address])
        self.sold_tokens += token_amount
      else:
        fails("Preallocate fails", tx_hash)
  
  def send_ether(self, buyer):
    tx_hash = self.send_ether_to_crowdsale(buyer.address, self.investment)
    if self.halted:
      fails("Sending ether to crowdsale fails if halted", tx_hash)
    elif self.requiredCustomerId:
      fails("Sending ether to crowdsale fails with requiredCustomerId", tx_hash)
    elif (self.states["PreFunding"] == self.state and not buyer.whitelisted):
      fails("Sending ether to crowdsale fails if in PreFunding state and buyer isn't whitelisted", tx_hash)
    elif (self.states["PreFunding"] != self.state and self.states["Funding"] != self.state):
      fails("Sending ether to crowdsale fails if not in PreFunding nor Funding state", tx_hash)
    else:
      succeeds("Sending ether to crowdsale succeeds", tx_hash)
      (wei_amount, token_amount) = self.calculate_token_amount(self.investment * (10 ** 18), buyer.address)
      self.multisig_wei += wei_amount
      self.token_balances[buyer.address] += token_amount
      print(buyer.address)
      print(buyer.whitelisted)
      print(self.token_balance(buyer.address))
      print(self.token_balances[buyer.address])
      self.sold_tokens += token_amount

  def buy(self, buyer):
    tx_hash = super().buy(buyer.address, self.investment)
    if self.halted:
      fails("Buying using buy fails if halted", tx_hash)
    elif self.requiredCustomerId:
      fails("Buying using buy fails with requiredCustomerId", tx_hash)
    elif (self.states["PreFunding"] == self.state and not buyer.whitelisted):
      fails("Buying using buy fails if in PreFunding state and buyer isn't whitelisted", tx_hash)
    elif (self.states["PreFunding"] != self.state and self.states["Funding"] != self.state):
      fails("Buying using buy fails if not in PreFunding nor Funding state", tx_hash)
    else:
      succeeds("Buying using buy succeeds", tx_hash)
      (wei_amount, token_amount) = self.calculate_token_amount(self.investment * (10 ** 18), buyer.address)
      self.multisig_wei += wei_amount
      self.token_balances[buyer.address] += token_amount
      print(buyer.address)
      print(buyer.whitelisted)
      print(self.token_balance(buyer.address))
      print(self.token_balances[buyer.address])
      self.sold_tokens += token_amount

  def buy_on_behalf(self, buyer, receiver):
    tx_hash = super().buy_on_behalf(buyer.address, receiver.address, self.investment)
    if self.halted:
      fails("Buying using buyOnBehalf fails if halted", tx_hash)
    elif self.requiredCustomerId:
      fails("Buying using buyOnBehalf fails with requiredCustomerId", tx_hash)
    elif (self.states["PreFunding"] == self.state and not buyer.whitelisted):
      fails("Buying using buyOnBehalf fails if in PreFunding state and buyer isn't whitelisted", tx_hash)
    elif (self.states["PreFunding"] != self.state and self.states["Funding"] != self.state):
      fails("Buying using buyOnBehalf fails if not in PreFunding nor Funding state", tx_hash)
    else:
      succeeds("Buying using buyOnBehalf succeeds", tx_hash)
      (wei_amount, token_amount) = self.calculate_token_amount(self.investment * (10 ** 18), buyer.address)
      self.multisig_wei += wei_amount
      self.token_balances[buyer.address] += token_amount
      print(buyer.address)
      print(buyer.whitelisted)
      print(self.token_balance(buyer.address))
      print(self.token_balances[buyer.address])
      self.sold_tokens += token_amount
  
  def buy_on_behalf_with_customer_id(self, buyer, receiver):
    tx_hash = super().buy_on_behalf_with_customer_id(buyer.address, receiver.address, buyer.customerId, self.investment)
    if self.halted:
      fails("Buying using buyOnBehalfWithCustomerId fails if halted", tx_hash)
    elif buyer.customerId == 0:
      fails("Buying using buyOnBehalfWithCustomerId fails with invalid customer ID", tx_hash)
    elif (self.states["PreFunding"] == self.state and not buyer.whitelisted):
      fails("Buying using buyOnBehalfWithCustomerId fails if in PreFunding state and buyer isn't whitelisted", tx_hash)
    elif (self.states["PreFunding"] != self.state and self.states["Funding"] != self.state):
      fails("Buying using buyOnBehalfWithCustomerId fails if not in PreFunding nor Funding state", tx_hash)
    else:
      succeeds("Buying using buyOnBehalfWithCustomerId succeeds", tx_hash)
      (wei_amount, token_amount) = self.calculate_token_amount(self.investment * (10 ** 18), buyer.address)
      self.multisig_wei += wei_amount
      self.token_balances[buyer.address] += token_amount
      print(buyer.address)
      print(buyer.whitelisted)
      print(self.token_balance(buyer.address))
      print(self.token_balances[buyer.address])
      self.sold_tokens += token_amount
  
  def buy_with_customer_id(self, buyer):
    tx_hash = super().buy_with_customer_id(buyer.customerId, buyer.address, self.investment)
    if self.halted:
      fails("Buying using buyOnBehalfWithCustomerId fails if halted", tx_hash)
    elif buyer.customerId == 0:
      fails("Buying using buyOnBehalfWithCustomerId fails with invalid customer ID", tx_hash)
    elif (self.states["PreFunding"] == self.state and not buyer.whitelisted):
      fails("Buying using buyOnBehalfWithCustomerId fails if in PreFunding state and buyer isn't whitelisted", tx_hash)
    elif (self.states["PreFunding"] != self.state and self.states["Funding"] != self.state):
      fails("Buying using buyOnBehalfWithCustomerId fails if not in PreFunding nor Funding state", tx_hash)
    else:
      succeeds("Buying using buyOnBehalfWithCustomerId succeeds", tx_hash)
      (wei_amount, token_amount) = self.calculate_token_amount(self.investment * (10 ** 18), buyer.address)
      self.multisig_wei += wei_amount
      self.token_balances[buyer.address] += token_amount
      print(buyer.address)
      print(buyer.whitelisted)
      print(self.token_balance(buyer.address))
      print(self.token_balances[buyer.address])
      self.sold_tokens += token_amount
  
  def try_buys(self):
    for x in self.investors:
      self.send_ether(x)
      self.buy(x)
      self.buy_with_customer_id(x)

    for y in self.investors:
      for x in self.investors:
        self.buy_on_behalf(x,y)
        self.buy_on_behalf_with_customer_id(x,y)