#!/usr/bin/env python3

import sys
sys.path.append("../deployment")
from deployer import Deployer
from web3_interface import Web3Interface
from tx_checker import fails, succeeds

web3 = Web3Interface().w3
web3.miner.start(1)
deployer = Deployer()
accounts = web3.eth.accounts
sender = accounts[0]
gas = 50000000
gas_price = 20000000000
tx = {"from": sender, "value": 0, "gas": gas, "gasPrice": gas_price}

(standard_token_contract, tx_hash) = deployer.deploy("./build/", "StandardTokenMock", tx,)
receipt = web3.eth.waitForTransactionReceipt(tx_hash)
assert receipt.status == 1
functions = standard_token_contract.functions
token_balances = {x : 0 for x in accounts}
allowed = {i : {x : 0 for x in accounts} for i in accounts}
total_supply = 0
value_transfer = 10000
value_mint = 100000

def get_total_supply():
  return functions.totalSupply().call()
def balance_of(address):
  return functions.balanceOf(address).call()
def allowance(account, spender):
  return functions.allowance(account, spender).call()
def get_balance(address):
  return web3.eth.getBalance(address)
def sub_approval(allower, spender, value):
  old = allowed[allower][spender]
  if value > old:
    allowed[allower][spender] = 0
  else:
    allowed[allower][spender] = old - value
def test_balances():
  assert total_supply == get_total_supply()
  for x in accounts:
    assert token_balances[x] == balance_of(x)
  for n in accounts:
    for m in accounts:
      assert allowed[n][m] == allowance(n, m)

tx["from"] = accounts[3]
fails("Transfer 10000 from account 1 to account 2 with account 3: Fails because account 1 has no tokens", functions.transferFrom(accounts[1], accounts[2], value_transfer).transact(tx))

tx["from"] = accounts[1]
fails("Transfer 10000 from account 1 to account 2: Fails because account 1 has no tokens", functions.transfer(accounts[2], value_transfer).transact(tx))

fails("Burn 10000 from account 1: Fails because account 1 has no tokens", functions.burnTokensMock(accounts[1], value_transfer).transact(tx))

succeeds("subApproval of 10000 from account 1 to account 2: Succeeds because it has no restrictions", functions.subApproval(accounts[2], value_transfer).transact(tx))
sub_approval(accounts[1], accounts[2], value_transfer)

succeeds("addApproval of 10000 from account 1 to account 2: Succeeds because it has no restrictions", functions.addApproval(accounts[2], value_transfer).transact(tx))
allowed[accounts[1]][accounts[2]] += value_transfer

fails("Approve 10000 from account 1 to account 2: Fails because neither value or allowance are zero", functions.approve(accounts[2], value_transfer).transact(tx))

succeeds("Mint 100000 to account 1: Succeeds because mint has no restrictions", functions.mint(accounts[1], value_mint).transact(tx))
token_balances[accounts[1]] += value_mint
total_supply += value_mint

succeeds("Transfer 10000 from account 1 to account 2: Succeeds because account 1 has tokens", functions.transfer(accounts[2], value_transfer).transact(tx))
token_balances[accounts[1]] -= value_transfer
token_balances[accounts[2]] += value_transfer

tx["from"] = accounts[3]
fails("Transfer 10000 from account 1 to account 2 with account 3: Fails because account 3 has no allowance", functions.transferFrom(accounts[1], accounts[2], value_transfer).transact(tx))

tx["from"] = accounts[2]
succeeds("Transfer 10000 from account 1 to account 3 with account 2: Succeeds because account 2 has enough allowance", functions.transferFrom(accounts[1], accounts[3], value_transfer).transact(tx))
token_balances[accounts[1]] -= value_transfer
token_balances[accounts[3]] += value_transfer
allowed[accounts[1]][accounts[2]] -= value_transfer

succeeds("Approve 10000 from account 2 to account 3: Succeeds because allowance == 0", functions.approve(accounts[3], value_transfer).transact(tx))
allowed[accounts[2]][accounts[3]] += value_transfer

succeeds("Burn 10000 from account 1: Succeeds because account 1 has tokens", functions.burnTokensMock(accounts[1], value_transfer).transact(tx))
token_balances[accounts[1]] -= value_transfer
total_supply -= value_transfer

test_balances()