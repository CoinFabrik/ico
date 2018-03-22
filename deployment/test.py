#!/usr/bin/python3 -i

import deploy
from setConfig import wait, dump, time, params, miner, accounts, web3
from testing_helpers import Crowdsale, Token

def to_32byte_hex(val):
  return web3.toHex(web3.toBytes(val).rjust(32, b'\0'))


def fails(message, tx_receipt):
  print(message, end='')
  try:
    assert tx_receipt.status == 0
  except Exception as e:
    print(" ✗✘")
    raise "Transaction expected to fail succeeded"
  else:
    print(" ✓✔")

def succeeds(message, tx_receipt):
  print(message, end='')
  try:
    assert tx_receipt.status == 1
  except Exception as e:
    print(" ✗✘")
    raise "Transaction expected to succeed failed"
  else:
    print(" ✓✔")


# Dict with the states for comparison
states = {"Unknown": 0, "PendingConfiguration": 1, "PreFunding": 2, "Funding": 3, "Success": 4, "Finalized": 5}

address_zero = '0x0000000000000000000000000000000000000000'

message = "[Etherscan.io 26/02/2018 19:26:08] I, hereby verify that the information provided is accurate and I am the owner/creator of the token contract address 0xF87F0D9153fea549c728Ad61cb801595a68b73de"
hashed_message = web3.sha3(text=message)

signer = accounts[0]
address_to_sign = accounts[1]

signature_hexbytes = web3.eth.sign(signer, text=message)

signature = signature_hexbytes.hex()

r = signature[:66]
s = '0x' + signature[66:130]
v = '0x' + signature[130:132]
v = web3.toInt(hexstr=v)

tokens_to_preallocate = 10

# Testing start ----------------------------------------------------------

# Pre-configuration testing


print("Creating crowdsale object")
crowdsale = Crowdsale(params) 
print("\nCrowdsale object created.")

assert states['PendingConfiguration'] == crowdsale.get_state(), "State should be PendingConfiguration"

succeeds("configurationCrowdsale function",
  crowdsale.configuration_crowdsale())

tranches = crowdsale.contract.functions.tranches(0).call()
time.sleep(max(tranches[1] - time.time(), 0))


# Post-configuration testing


# Token object creation
print("Creating token object")
token = Token(crowdsale.contract)


# Testing getTranchesLength function
print("Testing getTranchesLength function:", end=' ')
result = crowdsale.get_tranches_length()
print(str(result))

assert states['PreFunding'] == crowdsale.get_state(), "State should be PreFunding"

succeeds("Set signer address but does not require sign",
  crowdsale.set_require_signed_address(False, signer))

succeeds("Whitelists an address",
  crowdsale.set_early_participant_whitelist(accounts[1], True))

succeeds("Whitelists another address",
  crowdsale.set_early_participant_whitelist(accounts[3], True))

print("Test reading earlyParticipantWhitelist mapping for accounts[1]")
result = crowdsale.early_participant_whitelist(accounts[1])
print("\nTest reading earlyParticipantWhitelist mapping result: " + str(result))

print("Test reading earlyParticipantWhitelist mapping for accounts[3]")
result = crowdsale.early_participant_whitelist(accounts[3])
print("\nTest reading earlyParticipantWhitelist mapping result: " + str(result))

print("Test reading transferAgents mapping for Crowdsale Address")
result = token.transfer_agents(crowdsale.contract.address)
print("\nTest reading transferAgents mapping result: " + str(result))

# Testing buying functions
balance = token.balance_of(accounts[1])
succeeds("Buys using a whitelisted address through fallback function",
  crowdsale.send_ether_to_crowdsale(accounts[1], 2))
assert token.balance_of(accounts[1]) > balance

balance = token.balance_of(accounts[2])
fails("Buys using a non-whitelisted address through fallback function",
  crowdsale.send_ether_to_crowdsale(accounts[2], 2))
assert token.balance_of(accounts[2]) == balance

balance = token.balance_of(accounts[1])
succeeds("Buys using a whitelisted address through buy",
  crowdsale.buy(accounts[1], 2))
assert token.balance_of(accounts[1]) > balance

balance = token.balance_of(accounts[2])
fails("Buys using a non-whitelisted address through buy",
  crowdsale.buy(accounts[2], 2))
assert token.balance_of(accounts[2]) == balance

balance = token.balance_of(accounts[1])
succeeds("Buys on behalf of itself using a whitelisted address through buyOnBehalf",
  crowdsale.buy_on_behalf(accounts[1], accounts[1], 2))
assert token.balance_of(accounts[1]) > balance

balance = token.balance_of(accounts[3])
succeeds("Buys on behalf of another whitelisted address using a whitelisted address through buyOnBehalf",
  crowdsale.buy_on_behalf(accounts[1], accounts[3], 2))
assert token.balance_of(accounts[3]) > balance

balance = token.balance_of(accounts[1])
fails("Buys on behalf of a whitelisted address using a non-whitelisted address through buyOnBehalf",
  crowdsale.buy_on_behalf(accounts[2], accounts[1], 2))
assert token.balance_of(accounts[1]) == balance

balance = token.balance_of(accounts[2])
fails("Buys on behalf of itself using a non-whitelisted address through buyOnBehalf",
  crowdsale.buy_on_behalf(accounts[2], accounts[2], 2))
assert token.balance_of(accounts[2]) == balance

balance = token.balance_of(accounts[1])
succeeds("Buys with buyOnBehalfWithCustomerId function with whitelisted address.",
  crowdsale.buy_on_behalf_with_customer_id(accounts[1], 1, 2))
assert token.balance_of(accounts[1]) > balance

#balance = token.balance_of(accounts[1])
# Testing buyOnBehalfWithSignedAddress function
#print("Testing buyOnBehalfWithSignedAddress function with accounts[1]. Should work because it's whitelisted")
#receipt = crowdsale.buy_on_behalf_with_signed_address(accounts[1], 1, v, r, s, 2)
#print("\nTesting buyOnBehalfWithSignedAddress function successful: " + str(receipt.status == 1))
#assert token.balance_of(accounts[1]) > balance

balance = token.balance_of(accounts[1])
succeeds("Buys with buyWithCustomerId function with whitelisted address.",
    crowdsale.buy_with_customer_id(1, accounts[1], 2))
assert token.balance_of(accounts[1]) > balance

#balance = token.balance_of(accounts[1])

# Testing buyWithSignedAddress function
#print("Testing buyWithSignedAddress function with accounts[1]. Should work because it's whitelisted")
#receipt = crowdsale.buy_with_signed_address(1, v, r, s, accounts[1], 2)
#print("\nTesting buyWithSignedAddress function successful: " + str(receipt.status == 1))


#assert token.balance_of(accounts[1]) > balance

balance = token.balance_of(accounts[2])
succeeds("Testing preallocate function",
  crowdsale.preallocate(accounts[2], tokens_to_preallocate, 350))
assert token.balance_of(accounts[2]) > balance
print("\nAssert 1 successful")
assert token.balance_of(accounts[2]) == (tokens_to_preallocate * (10 ** 18))
print("\nAssert 2 successful")


crowdsale.start_ico()
print("ICO STARTS")


balance = token.balance_of(accounts[1])
succeeds("Test sending ether to crowdsale from accounts[1]. Should work because it's whitelisted",
  crowdsale.send_ether_to_crowdsale(accounts[1], 2))
assert token.balance_of(accounts[1]) > balance

balance = token.balance_of(accounts[1])
succeeds("Testing buy function with accounts[1]. Should work because it's whitelisted",
  crowdsale.buy(accounts[1], 2))
assert token.balance_of(accounts[1]) > balance

balance = token.balance_of(accounts[1])
succeeds("Testing buyOnBehalf function with accounts[1]. Should work because it's whitelisted",
  crowdsale.buy_on_behalf(accounts[1], 2))
assert token.balance_of(accounts[1]) > balance

balance = token.balance_of(accounts[1])
succeeds("Testing buyOnBehalfWithCustomerId function with accounts[1]. Should work because it's whitelisted",
  crowdsale.buy_on_behalf_with_customer_id(accounts[1], 1, 2))
assert token.balance_of(accounts[1]) > balance

balance = token.balance_of(accounts[2])
succeeds("Testing preallocate function",
  crowdsale.preallocate(accounts[2], tokens_to_preallocate, 350))
assert token.balance_of(accounts[2]) > balance
print("\nAssert 1 successful")
assert token.balance_of(accounts[2]) == (balance + (tokens_to_preallocate * (10 ** 18)))
print("\nAssert 2 successful")

#print("Testing finalize function")
#receipt = crowdsale.finalize()
#print("\nTesting finalize function successful: " + str(receipt.status == 1))

miner.stop()