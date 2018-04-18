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
  ether = 2
  startsAt = None
  endsAt = None
  bounties_tokens = None
  multisig_wei = 0
  multisig_tokens = 0
  milieurs_per_eth = None
  priceAgent = None
  minimum_buy_value = None
  token = None
  token_balances = None
  tokens_sold_var = 0

  def __init__(self, params):
    Crowdsale.__init__(self, params)
    self.state = self.states["PendingConfiguration"]
    self.investors.append(Investor(self.accounts[1], True, 0))
    self.investors.append(Investor(self.accounts[2], True, 1))
    self.investors.append(Investor(self.accounts[3], False, 0))
    self.investors.append(Investor(self.accounts[4], False, 1))
    self.token_balances = {x : 0 for x in self.accounts}
    self.multisig_wei = self.web3.eth.getBalance(super().multisig_wallet())
    print(self.multisig_wei)
    print(self.web3.eth.getBalance(super().multisig_wallet()))
  
  def set_early_participant_whitelist(self):
    succeeds("Whitelist Account 1", super().set_early_participant_whitelist(self.accounts[1], True))
    succeeds("Whitelist Account 2", super().set_early_participant_whitelist(self.accounts[2], True))  
  
  def require_customer_id(self):
    succeeds("Require Customer ID", super().set_require_customer_id(True))
    self.requiredCustomerId = True

  def unrequire_customer_id(self):
    succeeds("Unrequire Customer ID", super().set_require_customer_id(False))
    self.requiredCustomerId = False

  def require_signed_address(self, signer):
    succeeds("Require Signed Address", super().set_require_signed_address(True, signer))
    self.signer = signer
    self.requiredSignedAddress = True

  def require_signed_address(self, signer):
    succeeds("Unrequire Signed Address", super().set_require_signed_address(False, signer))
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
    assert super().get_state() == self.state
  
  def try_finalize(self):
    if self.state == self.states["Success"] and not self.halted:
      succeeds("Finalization of Crowdsale succeeds", super().finalize())
      self.state = self.states["Finalized"]
      sold = self.tokens_sold_var + self.bounties_tokens
      to_share = (sold * 18) // 82
      self.multisig_tokens += to_share
      self.check_all_end_balances()
    else:
      fails("Finalization of Crowdsale fails", super().finalize())
  
  def instantiate_token(self):
    loader = ContractLoader()
    contract = loader.load("./build/", "CrowdsaleToken", contract_address=super().token())
    return contract

  def check_all_end_balances(self):
    assert self.web3.eth.getBalance(super().multisig_wallet()) == self.multisig_wei
    assert self.token_balance(super().multisig_wallet()) == self.multisig_tokens
    assert self.crowdsale_balance() == 0
    for account in self.accounts:
      assert self.token_balance(account) == self.token_balances[account]

  def token_balance(self, address):
    return self.token.functions.balanceOf(address).call()

  def crowdsale_balance(self):
    return self.web3.eth.getBalance(self.contract.address)

  def try_configuration_crowdsale(self):
    if self.state == self.states["PendingConfiguration"]:
      succeeds("Configuration of Crowdsale succeeds", super().configuration_crowdsale())
      self.state = self.states["PreFunding"]
      self.startsAt = super().starts_at()
      self.endsAt = super().ends_at()
      self.bounties_tokens = self.multisig_tokens = super().initial_bounties_tokens()
      self.token = self.instantiate_token()
      try:
        assert self.token_balance(super().multisig_wallet()) == 252 * (10 ** 5) * (10 ** 18)
        assert self.token_balance(self.contract.address) == 1008 * (10 ** 6) * (10 ** 18)
        assert self.token_balance(super().multisig_wallet()) == self.params["multisig_supply"]
        assert self.token_balance(self.contract.address) == self.params["crowdsale_supply"]
      except AssertionError:
        print("Assertion Error")
    else:
      fails("Configuration of Crowdsale fails", super().configuration_crowdsale())
    print("ETA for ICO: " + str(super().eta_ico() + 1) + " seconds.")
    
  def try_set_starting_time(self, starting_time):
    if self.state == self.states["PreFunding"] and int(round(time.time())) < starting_time and starting_time < super().ends_at():
      succeeds("Set starting time succeeds", super().set_starting_time(starting_time))
      self.startsAt = starting_time
    else:
      fails("Set starting time fails", super().set_starting_time(starting_time))
  
  def try_set_ending_time(self, ending_time):
    if (self.state == self.states["PreFunding"] or self.state == self.states["Funding"]) and int(round(time.time())) < ending_time and super().starts_at() < ending_time:
      succeeds("Set starting time succeeds", super().set_ending_time(ending_time))
      self.endsAt = ending_time
    else:
      fails("Set starting time fails", super().set_ending_time(ending_time))

  def try_update_eurs_per_eth(self, milieurs_amount, price_agent):
    if (self.state == self.states["PreFunding"] or self.state == self.states["Funding"]) and self.priceAgent == price_agent:
      succeeds("Update eurs per eth succeeds", super().update_eurs_per_eth(milieurs_amount))
      self.milieurs_per_eth = milieurs_amount
    else:
      fails("Update eurs per eth fails", super().update_eurs_per_eth(milieurs_amount))

  def try_update_price_agent(self, new_price_agent):
    if (self.state == self.states["PreFunding"] or self.state == self.states["Funding"]):
      succeeds("Update price agent succeeds", super().update_price_agent(new_price_agent))
      self.priceAgent = new_price_agent
    else:
      fails("Update price agent fails", super().update_price_agent(new_price_agent))

  def try_set_minimum_buy_value(self, new_minimum):
    if (self.state == self.states["PreFunding"] or self.state == self.states["Funding"]):
      succeeds("Set minimum buy value succeeds", super().set_minimum_buy_value(new_minimum))
      self.minimum_buy_value = new_minimum
    else:
      fails("Set minimum buy value fails", super().set_minimum_buy_value(new_minimum))

  def calculate_token_amount(self, wei_amount, receiver):
    token_amount = None
    tokens_per_eth = super().get_current_price() * super().milieurs_per_eth() // 1000
    max_wei_allowed = (super().sellable_tokens() - super().tokens_sold()) * (10 ** 18) // tokens_per_eth
    wei_allowed = min(max_wei_allowed, wei_amount)
    if wei_amount < max_wei_allowed:
      token_amount = tokens_per_eth * wei_amount // (10**18)
    else:
      token_amount = super().sellable_tokens() - super().tokens_sold()
    assert (self.token_balance(receiver) + token_amount) >= super().minimum_buy_value()
    return (wei_allowed, token_amount)

  def try_preallocate(self):
    for investor in self.investors:
      tx_receipt = super().preallocate(investor.address, self.tokens_to_preallocate, self.wei_price_of_preallocation)
      if self.state == self.states["PreFunding"] or self.state == self.states["Funding"]:
        succeeds("Preallocate succeeds", tx_receipt)
        token_amount = self.tokens_to_preallocate * (10**18)
        self.token_balances[investor.address] += token_amount
        self.tokens_sold_var += token_amount
      else:
        fails("Preallocate fails", tx_receipt)

  # Buy functions
  def send_ether(self, buyer):
    tx_receipt = super().send_ether_to_crowdsale(buyer.address, self.ether)
    if self.halted:
      fails("Sending ether to crowdsale fails if halted", tx_receipt)
    elif self.requiredCustomerId:
      fails("Sending ether to crowdsale fails with requiredCustomerId", tx_receipt)
    elif (self.states["PreFunding"] == self.state and not buyer.whitelisted):
      fails("Sending ether to crowdsale fails if in PreFunding state and buyer isn't whitelisted", tx_receipt)
    elif (self.states["PreFunding"] != self.state and self.states["Funding"] != self.state):
      fails("Sending ether to crowdsale fails if not in PreFunding nor Funding state", tx_receipt)
    else:
      succeeds("Sending ether to crowdsale succeeds", tx_receipt)
      (wei_amount, token_amount) = self.calculate_token_amount(self.ether * (10**18), buyer.address)
      self.multisig_wei += wei_amount
      print(self.multisig_wei)
      print(self.web3.eth.getBalance(super().multisig_wallet()))
      self.token_balances[buyer.address] += token_amount
      self.tokens_sold_var += token_amount

  def buy(self, buyer):
    tx_receipt = super().buy(buyer.address, self.ether)
    if self.halted:
      fails("Buying using buy fails if halted", tx_receipt)
    elif self.requiredCustomerId:
      fails("Buying using buy fails with requiredCustomerId", tx_receipt)
    elif (self.states["PreFunding"] == self.state and not buyer.whitelisted):
      fails("Buying using buy fails if in PreFunding state and buyer isn't whitelisted", tx_receipt)
    elif (self.states["PreFunding"] != self.state and self.states["Funding"] != self.state):
      fails("Buying using buy fails if not in PreFunding nor Funding state", tx_receipt)
    else:
      succeeds("Buying using buy succeeds", tx_receipt)
      (wei_amount, token_amount) = self.calculate_token_amount(self.ether * (10**18), buyer.address)
      self.multisig_wei += wei_amount
      print(self.multisig_wei)
      print(self.web3.eth.getBalance(super().multisig_wallet()))
      self.token_balances[buyer.address] += token_amount
      self.tokens_sold_var += token_amount

  def buy_on_behalf(self, buyer, receiver):
    tx_receipt = super().buy_on_behalf(buyer.address, receiver.address, self.ether)
    if self.halted:
      fails("Buying using buyOnBehalf fails if halted", tx_receipt)
    elif self.requiredCustomerId:
      fails("Buying using buyOnBehalf fails with requiredCustomerId", tx_receipt)
    elif (self.states["PreFunding"] == self.state and not buyer.whitelisted):
      fails("Buying using buyOnBehalf fails if in PreFunding state and buyer isn't whitelisted", tx_receipt)
    elif (self.states["PreFunding"] != self.state and self.states["Funding"] != self.state):
      fails("Buying using buyOnBehalf fails if not in PreFunding nor Funding state", tx_receipt)
    else:
      succeeds("Buying using buyOnBehalf succeeds", tx_receipt)
      (wei_amount, token_amount) = self.calculate_token_amount(self.ether * (10**18), receiver.address)
      self.multisig_wei += wei_amount
      print(self.multisig_wei)
      print(self.web3.eth.getBalance(super().multisig_wallet()))
      self.token_balances[receiver.address] += token_amount
      self.tokens_sold_var += token_amount
  
  def buy_on_behalf_with_customer_id(self, buyer, receiver):
    tx_receipt = super().buy_on_behalf_with_customer_id(buyer.address, receiver.address, buyer.customerId, self.ether)
    if self.halted:
      fails("Buying using buyOnBehalfWithCustomerId fails if halted", tx_receipt)
    elif buyer.customerId == 0:
      fails("Buying using buyOnBehalfWithCustomerId fails with invalid customer ID", tx_receipt)
    elif (self.states["PreFunding"] == self.state and not buyer.whitelisted):
      fails("Buying using buyOnBehalfWithCustomerId fails if in PreFunding state and buyer isn't whitelisted", tx_receipt)
    elif (self.states["PreFunding"] != self.state and self.states["Funding"] != self.state):
      fails("Buying using buyOnBehalfWithCustomerId fails if not in PreFunding nor Funding state", tx_receipt)
    else:
      succeeds("Buying using buyOnBehalfWithCustomerId succeeds", tx_receipt)
      (wei_amount, token_amount) = self.calculate_token_amount(self.ether * (10**18), receiver.address)
      self.multisig_wei += wei_amount
      print(self.multisig_wei)
      print(self.web3.eth.getBalance(super().multisig_wallet()))
      self.token_balances[receiver.address] += token_amount
      self.tokens_sold_var += token_amount
  
  def buy_with_customer_id(self, buyer):
    tx_receipt = super().buy_with_customer_id(buyer.customerId, buyer.address, self.ether)
    if self.halted:
      fails("Buying using buyOnBehalfWithCustomerId fails if halted", tx_receipt)
    elif buyer.customerId == 0:
      fails("Buying using buyOnBehalfWithCustomerId fails with invalid customer ID", tx_receipt)
    elif (self.states["PreFunding"] == self.state and not buyer.whitelisted):
      fails("Buying using buyOnBehalfWithCustomerId fails if in PreFunding state and buyer isn't whitelisted", tx_receipt)
    elif (self.states["PreFunding"] != self.state and self.states["Funding"] != self.state):
      fails("Buying using buyOnBehalfWithCustomerId fails if not in PreFunding nor Funding state", tx_receipt)
    else:
      succeeds("Buying using buyOnBehalfWithCustomerId succeeds", tx_receipt)
      (wei_amount, token_amount) = self.calculate_token_amount(self.ether * (10**18), buyer.address)
      self.multisig_wei += wei_amount
      print(self.multisig_wei)
      print(self.web3.eth.getBalance(super().multisig_wallet()))
      self.token_balances[buyer.address] += token_amount
      self.tokens_sold_var += token_amount

  
  def try_buys(self):
    for x in self.investors:
      self.send_ether(x)
      self.buy(x)
      self.buy_with_customer_id(x)

    for y in self.investors:
      for x in self.investors:
        self.buy_on_behalf(x,y)
        self.buy_on_behalf_with_customer_id(x,y)