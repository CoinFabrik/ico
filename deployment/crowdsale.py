#!/usr/bin/python3 -i
from web3 import Web3, HTTPProvider
import itertools
import json
import time

web3 = Web3(HTTPProvider('http://localhost:8545'))

eth = web3.eth

contract_name = "Crowdsale"

with open("build/" + contract_name + ".abi") as contract_abi_file:
  contract_abi = json.load(contract_abi_file)

#Comes as string without '0x'
contract_bin = open("build/" + contract_name + ".bin").read()
contract = eth.contract(contract_abi, bytecode=("0x" + contract_bin))

with open("build/CrowdsaleToken.abi") as token_abi_file:
  token_abi = json.load(token_abi_file)

token_contract = eth.contract(token_abi)

def trans(from_index=0, value=0):
  return {"from": eth.accounts[from_index], "value": value*(10**18), "gas": 4700000, "gasPrice": 50000000000}

#tokens_per_wei = [30*(10**25), 35*(10**25), 40*(10**25), 45*(10**25), 50*(10**25), 55*(10**25), 60*(10**25)]
#amounts = [10000000000000000000, 9090909090909090909, 8333333333333333333, 7142857142857142857, 5882352941176470588, 5000000000000000000, 4000000000000000000]

tokens_per_wei = [2]
amounts = [525 * (10 ** 5) * (10 **18)]

assert len(tokens_per_wei) == len(amounts)

one_year = 60*60*24*365
start = int(time.time()) + 60*2000
end = start + one_year

start_times = [start] * len(tokens_per_wei)
end_times = [end] * len(tokens_per_wei)

mw_address = "0xCAF3CAF3CAF3CAF3CAF3CAF3CAF3CAF3CAF3CAF3"
token_retriever = eth.accounts[1]
tranches = list(itertools.chain.from_iterable(zip(amounts, start_times, end_times, tokens_per_wei)))
print(tranches)
params = [mw_address, start, end, token_retriever, tranches]


#dHash = contract.deploy(transaction=trans(1,0), args=params)

def status(tx_receipt):
  time.sleep(2)
  return eth.getTransactionReceipt(tx_receipt)["status"]

def addAddress():
  #receipt = eth.getTransactionReceipt(dHash)
  contract.address = "0x896e6F7aC97eded5c927123ef8Efdd8255727D26"
  print("Crowdsale:", contract.address)
  token_contract.address = token()
  print("Token:", token_contract.address)

def balance(investor):
  if isinstance(investor, str):
    return token_contract.call(trans()).balanceOf(investor)
  else:
    return token_contract.call(trans()).balanceOf(eth.accounts[investor])

def buy(buyer_index, value):
  return status(contract.transact(trans(buyer_index, value)).buy())

def end_now():
  new_ending = int(time.time()) + 5
  print(status(contract.transact(trans(0,0)).setEndingTime(new_ending)))
  time.sleep(2)
  print(status(contract.transact(trans(0,0)).finalize()))

def token():
  return contract.call().token()

def state():
  return contract.call().getState()

def balances():
  for i in range(len(eth.accounts)):
    print(balance(i))

time.sleep(2)
addAddress()
