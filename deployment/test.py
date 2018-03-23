#!/usr/bin/env python3

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

whitelisted_address1 = accounts[1]
whitelisted_address2 = accounts[3]
non_whitelisted_address1 = accounts[2]
non_whitelisted_address2 = accounts[4]






# Testing start ----------------------------------------------------------






# Pre-configuration testing


print("\nCreating crowdsale object")
crowdsale = Crowdsale(params) 
print("Crowdsale object created.")

assert states['PendingConfiguration'] == crowdsale.get_state(), "State should be PendingConfiguration"



fails("Failed preallocation of tokens with non-whitelisted address",
  crowdsale.preallocate(non_whitelisted_address1, tokens_to_preallocate, 350))

fails("Failed preallocation of tokens with whitelisted address",
  crowdsale.preallocate(whitelisted_address2, tokens_to_preallocate, 350))



fails("Failed crowdsale finalization", crowdsale.finalize())
assert crowdsale.finalized() == False



succeeds("Configurate Crowdsale",
  crowdsale.configuration_crowdsale())

assert states['PreFunding'] == crowdsale.get_state(), "State should be PreFunding"
print("ESTAMOS EN PRE-ICO!")


fails("Failed Crowdsale configuration",
  crowdsale.configuration_crowdsale())


fails("Failed crowdsale finalization", crowdsale.finalize())
assert crowdsale.finalized() == False



tranches = crowdsale.contract.functions.tranches(0).call()
time.sleep(max(tranches[1] - time.time(), 0))


# Post-configuration testing


# Token object creation
print("Creating token object")
token = Token(crowdsale.contract)
print("Token object created.")

# Testing getTranchesLength function
print("Get tranches length:", end=' ')
result = crowdsale.get_tranches_length()
print(str(result))



succeeds("Set signer address but does not require sign.",
  crowdsale.set_require_signed_address(False, signer))



succeeds("Whitelists an address.",
  crowdsale.set_early_participant_whitelist(whitelisted_address1, True))

succeeds("Whitelists another address.",
  crowdsale.set_early_participant_whitelist(whitelisted_address2, True))



print("Reading earlyParticipantWhitelist mapping for whitelisted_address1: ",
  str(crowdsale.early_participant_whitelist(whitelisted_address1)))

print("Reading earlyParticipantWhitelist mapping for whitelisted_address2: ",
  str(crowdsale.early_participant_whitelist(whitelisted_address2)))



print("Reading transferAgents mapping for Crowdsale Address: ",
  str(token.transfer_agents(crowdsale.contract.address)))






# Testing buying functions
balance = token.balance_of(whitelisted_address1)
succeeds("Buys using a whitelisted address through fallback function.",
  crowdsale.send_ether_to_crowdsale(whitelisted_address1, 2))
assert token.balance_of(whitelisted_address1) > balance

balance = token.balance_of(non_whitelisted_address1)
fails("Buys using a non-whitelisted address through fallback function.",
  crowdsale.send_ether_to_crowdsale(non_whitelisted_address1, 2))
assert token.balance_of(non_whitelisted_address1) == balance



balance = token.balance_of(whitelisted_address1)
succeeds("Buys using a whitelisted address through buy.",
  crowdsale.buy(whitelisted_address1, 2))
assert token.balance_of(whitelisted_address1) > balance

balance = token.balance_of(non_whitelisted_address1)
fails("Buys using a non-whitelisted address through buy.",
  crowdsale.buy(non_whitelisted_address1, 2))
assert token.balance_of(non_whitelisted_address1) == balance



balance = token.balance_of(whitelisted_address1)
succeeds("Buys on behalf of themself using a whitelisted address through buyOnBehalf.",
  crowdsale.buy_on_behalf(whitelisted_address1, whitelisted_address1, 2))
assert token.balance_of(whitelisted_address1) > balance

balance = token.balance_of(non_whitelisted_address1)
fails("Buys on behalf of themself using a non-whitelisted address through buyOnBehalf.",
  crowdsale.buy_on_behalf(non_whitelisted_address1, non_whitelisted_address1, 2))
assert token.balance_of(non_whitelisted_address1) == balance

balance = token.balance_of(whitelisted_address2)
succeeds("Buys on behalf of another whitelisted address using a whitelisted address through buyOnBehalf.",
  crowdsale.buy_on_behalf(whitelisted_address1, whitelisted_address2, 2))
assert token.balance_of(whitelisted_address2) > balance

balance = token.balance_of(non_whitelisted_address1)
succeeds("Buys on behalf of a non-whitelisted address using a whitelisted address through buyOnBehalf.",
  crowdsale.buy_on_behalf(whitelisted_address1, non_whitelisted_address1, 2))
assert token.balance_of(non_whitelisted_address1) > balance

balance = token.balance_of(whitelisted_address1)
fails("Buys on behalf of a whitelisted address using a non-whitelisted address through buyOnBehalf.",
  crowdsale.buy_on_behalf(non_whitelisted_address1, whitelisted_address1, 2))
assert token.balance_of(whitelisted_address1) == balance

balance = token.balance_of(non_whitelisted_address2)
fails("Buys on behalf of a non-whitelisted address using a non-whitelisted address through buyOnBehalf.",
  crowdsale.buy_on_behalf(non_whitelisted_address1, non_whitelisted_address2, 2))
assert token.balance_of(non_whitelisted_address2) == balance



balance = token.balance_of(whitelisted_address1)
succeeds("Buys on behalf of themself using a whitelisted address with valid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(whitelisted_address1, whitelisted_address1, 1, 2))
assert token.balance_of(whitelisted_address1) > balance

balance = token.balance_of(non_whitelisted_address1)
fails("Buys on behalf of themself using a non-whitelisted address with valid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(non_whitelisted_address1, non_whitelisted_address1, 1, 2))
assert token.balance_of(non_whitelisted_address1) == balance

balance = token.balance_of(whitelisted_address2)
succeeds("Buys on behalf of another whitelisted address using a whitelisted address with valid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(whitelisted_address1, whitelisted_address2, 1, 2))
assert token.balance_of(whitelisted_address2) > balance

balance = token.balance_of(non_whitelisted_address1)
succeeds("Buys on behalf of a non-whitelisted address using a whitelisted address with valid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(whitelisted_address1, non_whitelisted_address1, 1, 2))
assert token.balance_of(non_whitelisted_address1) > balance

balance = token.balance_of(whitelisted_address1)
fails("Buys on behalf of a whitelisted address using a non-whitelisted address with valid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(non_whitelisted_address1, whitelisted_address1, 1, 2))
assert token.balance_of(whitelisted_address1) == balance

balance = token.balance_of(non_whitelisted_address2)
fails("Buys on behalf of a non-whitelisted address using a non-whitelisted address with valid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(non_whitelisted_address1, non_whitelisted_address2, 1, 2))
assert token.balance_of(non_whitelisted_address2) == balance


balance = token.balance_of(whitelisted_address1)
fails("Buys on behalf of themself using a whitelisted address with invalid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(whitelisted_address1, whitelisted_address1, 0, 2))
assert token.balance_of(whitelisted_address1) == balance

balance = token.balance_of(non_whitelisted_address1)
fails("Buys on behalf of themself using a non-whitelisted address with invalid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(non_whitelisted_address1, non_whitelisted_address1, 0, 2))
assert token.balance_of(non_whitelisted_address1) == balance

balance = token.balance_of(whitelisted_address2)
fails("Buys on behalf of another whitelisted address using a whitelisted address with invalid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(whitelisted_address1, whitelisted_address2, 0, 2))
assert token.balance_of(whitelisted_address2) == balance

balance = token.balance_of(non_whitelisted_address1)
fails("Buys on behalf of a non-whitelisted address using a whitelisted address with invalid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(whitelisted_address1, non_whitelisted_address1, 0, 2))
assert token.balance_of(non_whitelisted_address1) == balance

balance = token.balance_of(whitelisted_address1)
fails("Buys on behalf of a whitelisted address using a non-whitelisted address with invalid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(non_whitelisted_address1, whitelisted_address1, 0, 2))
assert token.balance_of(whitelisted_address1) == balance

balance = token.balance_of(non_whitelisted_address2)
fails("Buys on behalf of a non-whitelisted address using a non-whitelisted address with invalid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(non_whitelisted_address1, non_whitelisted_address2, 0, 2))
assert token.balance_of(non_whitelisted_address2) == balance



#balance = token.balance_of(whitelisted_address1)
#succeeds("Buys with whitelisted address on behalf of a whitelisted, signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address2, whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) > balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with whitelisted address on behalf of a whitelisted, non-signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address2, whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#succeeds("Buys with whitelisted address on behalf of a non-whitelisted, signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address2, non_whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address1) > balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys with whitelisted address on behalf of a non-whitelisted, non-signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address2, non_whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with non-whitelisted address on behalf of a whitelisted, signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with non-whitelisted address on behalf of a whitelisted, non-signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address2)
#fails("Buys with non-whitelisted address on behalf of a non-whitelisted, signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, non_whitelisted_address2, 1, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address2) == balance
#
#balance = token.balance_of(non_whitelisted_address2)
#fails("Buys with non-whitelisted address on behalf of a non-whitelisted, non-signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, non_whitelisted_address2, 1, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address2) == balance
#
#balance = token.balance_of(whitelisted_address1)
#succeeds("Buys on behalf of themself with a whitelisted, signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address1, whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) > balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys on behalf of themself with a whitelisted, non-signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address1, whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys on behalf of themself with a non-whitelisted, signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, non_whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys on behalf of themself with a non-whitelisted, non-signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, non_whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with whitelisted address on behalf of a whitelisted, signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address2, whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with whitelisted address on behalf of a whitelisted, non-signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address2, whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys with whitelisted address on behalf of a non-whitelisted, signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address2, non_whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys with whitelisted address on behalf of a non-whitelisted, non-signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address2, non_whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with non-whitelisted address on behalf of a whitelisted, signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with non-whitelisted address on behalf of a whitelisted, non-signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address2)
#fails("Buys with non-whitelisted address on behalf of a non-whitelisted, signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, non_whitelisted_address2, 0, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address2) == balance
#
#balance = token.balance_of(non_whitelisted_address2)
#fails("Buys with non-whitelisted address on behalf of a non-whitelisted, non-signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, non_whitelisted_address2, 0, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address2) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys on behalf of themself with a whitelisted, signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address1, whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys on behalf of themself with a whitelisted, non-signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address1, whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys on behalf of themself with a non-whitelisted, signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, non_whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys on behalf of themself with a non-whitelisted, non-signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, non_whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address1) == balance



balance = token.balance_of(whitelisted_address1)
succeeds("Buys with whitelisted address and valid customerId with buyWithCustomerId.",
  crowdsale.buy_with_customer_id(1, whitelisted_address1, 2))
assert token.balance_of(whitelisted_address1) > balance

balance = token.balance_of(whitelisted_address1)
fails("Buys with whitelisted address and invalid customerId with buyWithCustomerId.",
  crowdsale.buy_with_customer_id(0, whitelisted_address1, 2))
assert token.balance_of(whitelisted_address1) == balance

balance = token.balance_of(non_whitelisted_address1)
fails("Buys with non-whitelisted address and valid customerId with buyWithCustomerId.",
  crowdsale.buy_with_customer_id(1, non_whitelisted_address1, 2))
assert token.balance_of(non_whitelisted_address1) == balance

balance = token.balance_of(non_whitelisted_address1)
fails("Buys with non-whitelisted address and invalid customerId with buyWithCustomerId.",
  crowdsale.buy_with_customer_id(0, non_whitelisted_address1, 2))
assert token.balance_of(non_whitelisted_address1) == balance



#balance = token.balance_of(whitelisted_address1)
#succeeds("Buys with whitelisted and signed address and valid customerId with buyWithSignedAddress",
#  crowdsale.buy_with_signed_address(1, v, r, s, whitelisted_address1, 2))
#assert token.balance_of(whitelisted_address1) > balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with whitelisted and signed address and invalid customerId with buyWithSignedAddress",
#  crowdsale.buy_with_signed_address(0, v, r, s, whitelisted_address1, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with whitelisted and unsigned address and valid customerId with buyWithSignedAddress",
#  crowdsale.buy_with_signed_address(1, v, r, s, whitelisted_address1, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with whitelisted and unsigned address and invalid customerId with buyWithSignedAddress",
#  crowdsale.buy_with_signed_address(0, v, r, s, whitelisted_address1, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys with non-whitelisted and signed address and valid customerId with buyWithSignedAddress",
#  crowdsale.buy_with_signed_address(1, v, r, s, non_whitelisted_address1, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys with non-whitelisted and signed address and invalid customerId with buyWithSignedAddress",
#  crowdsale.buy_with_signed_address(0, v, r, s, non_whitelisted_address1, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys with non-whitelisted and unsigned address and valid customerId with buyWithSignedAddress",
#  crowdsale.buy_with_signed_address(1, v, r, s, non_whitelisted_address1, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys with non-whitelisted and unsigned address and invalid customerId with buyWithSignedAddress",
#  crowdsale.buy_with_signed_address(0, v, r, s, non_whitelisted_address1, 2))
#assert token.balance_of(non_whitelisted_address1) == balance



balance = token.balance_of(non_whitelisted_address1)
succeeds("Preallocate tokens with non-whitelisted address",
  crowdsale.preallocate(non_whitelisted_address1, tokens_to_preallocate, 350))
assert token.balance_of(non_whitelisted_address1) > balance
assert token.balance_of(non_whitelisted_address1) == balance + (tokens_to_preallocate * (10 ** 18))

balance = token.balance_of(whitelisted_address2)
succeeds("Preallocate tokens with whitelisted address",
  crowdsale.preallocate(whitelisted_address2, tokens_to_preallocate, 350))
assert token.balance_of(whitelisted_address2) > balance
assert token.balance_of(whitelisted_address2) == balance + (tokens_to_preallocate * (10 ** 18))



crowdsale.start_ico()
assert states['Funding'] == crowdsale.get_state(), "State should be Funding"
print("ESTAMOS EN ICO!")



fails("Failed Crowdsale configuration",
  crowdsale.configuration_crowdsale())

fails("Failed Crowdsale finalization", crowdsale.finalize())
assert crowdsale.finalized() == False



# Testing buying functions
balance = token.balance_of(whitelisted_address1)
succeeds("Buys using a whitelisted address through fallback function.",
  crowdsale.send_ether_to_crowdsale(whitelisted_address1, 2))
assert token.balance_of(whitelisted_address1) > balance

balance = token.balance_of(non_whitelisted_address1)
succeeds("Buys using a non-whitelisted address through fallback function.",
  crowdsale.send_ether_to_crowdsale(non_whitelisted_address1, 2))
assert token.balance_of(non_whitelisted_address1) > balance



balance = token.balance_of(whitelisted_address1)
succeeds("Buys using a whitelisted address through buy.",
  crowdsale.buy(whitelisted_address1, 2))
assert token.balance_of(whitelisted_address1) > balance

balance = token.balance_of(non_whitelisted_address1)
succeeds("Buys using a non-whitelisted address through buy.",
  crowdsale.buy(non_whitelisted_address1, 2))
assert token.balance_of(non_whitelisted_address1) > balance



balance = token.balance_of(whitelisted_address1)
succeeds("Buys on behalf of themself using a whitelisted address through buyOnBehalf.",
  crowdsale.buy_on_behalf(whitelisted_address1, whitelisted_address1, 2))
assert token.balance_of(whitelisted_address1) > balance

balance = token.balance_of(non_whitelisted_address1)
succeeds("Buys on behalf of themself using a non-whitelisted address through buyOnBehalf.",
  crowdsale.buy_on_behalf(non_whitelisted_address1, non_whitelisted_address1, 2))
assert token.balance_of(non_whitelisted_address1) > balance

balance = token.balance_of(whitelisted_address2)
succeeds("Buys on behalf of another whitelisted address using a whitelisted address through buyOnBehalf.",
  crowdsale.buy_on_behalf(whitelisted_address1, whitelisted_address2, 2))
assert token.balance_of(whitelisted_address2) > balance

balance = token.balance_of(non_whitelisted_address1)
succeeds("Buys on behalf of a non-whitelisted address using a whitelisted address through buyOnBehalf.",
  crowdsale.buy_on_behalf(whitelisted_address1, non_whitelisted_address1, 2))
assert token.balance_of(non_whitelisted_address1) > balance

balance = token.balance_of(whitelisted_address1)
succeeds("Buys on behalf of a whitelisted address using a non-whitelisted address through buyOnBehalf.",
  crowdsale.buy_on_behalf(non_whitelisted_address1, whitelisted_address1, 2))
assert token.balance_of(whitelisted_address1) > balance

balance = token.balance_of(non_whitelisted_address2)
succeeds("Buys on behalf of a non-whitelisted address using a non-whitelisted address through buyOnBehalf.",
  crowdsale.buy_on_behalf(non_whitelisted_address1, non_whitelisted_address2, 2))
assert token.balance_of(non_whitelisted_address2) > balance



balance = token.balance_of(whitelisted_address1)
succeeds("Buys on behalf of themself using a whitelisted address with valid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(whitelisted_address1, whitelisted_address1, 1, 2))
assert token.balance_of(whitelisted_address1) > balance

balance = token.balance_of(non_whitelisted_address1)
succeeds("Buys on behalf of themself using a non-whitelisted address with valid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(non_whitelisted_address1, non_whitelisted_address1, 1, 2))
assert token.balance_of(non_whitelisted_address1) > balance

balance = token.balance_of(whitelisted_address2)
succeeds("Buys on behalf of another whitelisted address using a whitelisted address with valid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(whitelisted_address1, whitelisted_address2, 1, 2))
assert token.balance_of(whitelisted_address2) > balance

balance = token.balance_of(non_whitelisted_address1)
succeeds("Buys on behalf of a non-whitelisted address using a whitelisted address with valid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(whitelisted_address1, non_whitelisted_address1, 1, 2))
assert token.balance_of(non_whitelisted_address1) > balance

balance = token.balance_of(whitelisted_address1)
succeeds("Buys on behalf of a whitelisted address using a non-whitelisted address with valid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(non_whitelisted_address1, whitelisted_address1, 1, 2))
assert token.balance_of(whitelisted_address1) > balance

balance = token.balance_of(non_whitelisted_address2)
succeeds("Buys on behalf of a non-whitelisted address using a non-whitelisted address with valid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(non_whitelisted_address1, non_whitelisted_address2, 1, 2))
assert token.balance_of(non_whitelisted_address2) > balance


balance = token.balance_of(whitelisted_address1)
fails("Buys on behalf of themself using a whitelisted address with invalid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(whitelisted_address1, whitelisted_address1, 0, 2))
assert token.balance_of(whitelisted_address1) == balance

balance = token.balance_of(non_whitelisted_address1)
fails("Buys on behalf of themself using a non-whitelisted address with invalid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(non_whitelisted_address1, non_whitelisted_address1, 0, 2))
assert token.balance_of(non_whitelisted_address1) == balance

balance = token.balance_of(whitelisted_address2)
fails("Buys on behalf of another whitelisted address using a whitelisted address with invalid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(whitelisted_address1, whitelisted_address2, 0, 2))
assert token.balance_of(whitelisted_address2) == balance

balance = token.balance_of(non_whitelisted_address1)
fails("Buys on behalf of a non-whitelisted address using a whitelisted address with invalid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(whitelisted_address1, non_whitelisted_address1, 0, 2))
assert token.balance_of(non_whitelisted_address1) == balance

balance = token.balance_of(whitelisted_address1)
fails("Buys on behalf of a whitelisted address using a non-whitelisted address with invalid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(non_whitelisted_address1, whitelisted_address1, 0, 2))
assert token.balance_of(whitelisted_address1) == balance

balance = token.balance_of(non_whitelisted_address2)
fails("Buys on behalf of a non-whitelisted address using a non-whitelisted address with invalid customerId through buyOnBehalfWithCustomerId.",
  crowdsale.buy_on_behalf_with_customer_id(non_whitelisted_address1, non_whitelisted_address2, 0, 2))
assert token.balance_of(non_whitelisted_address2) == balance



#balance = token.balance_of(whitelisted_address1)
#succeeds("Buys with whitelisted address on behalf of a whitelisted, signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address2, whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) > balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with whitelisted address on behalf of a whitelisted, non-signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address2, whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#succeeds("Buys with whitelisted address on behalf of a non-whitelisted, signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address2, non_whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address1) > balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys with whitelisted address on behalf of a non-whitelisted, non-signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address2, non_whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with non-whitelisted address on behalf of a whitelisted, signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with non-whitelisted address on behalf of a whitelisted, non-signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address2)
#fails("Buys with non-whitelisted address on behalf of a non-whitelisted, signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, non_whitelisted_address2, 1, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address2) == balance
#
#balance = token.balance_of(non_whitelisted_address2)
#fails("Buys with non-whitelisted address on behalf of a non-whitelisted, non-signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, non_whitelisted_address2, 1, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address2) == balance
#
#balance = token.balance_of(whitelisted_address1)
#succeeds("Buys on behalf of themself with a whitelisted, signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address1, whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) > balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys on behalf of themself with a whitelisted, non-signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address1, whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys on behalf of themself with a non-whitelisted, signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, non_whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys on behalf of themself with a non-whitelisted, non-signed and with valid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, non_whitelisted_address1, 1, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with whitelisted address on behalf of a whitelisted, signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address2, whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with whitelisted address on behalf of a whitelisted, non-signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address2, whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys with whitelisted address on behalf of a non-whitelisted, signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address2, non_whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys with whitelisted address on behalf of a non-whitelisted, non-signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address2, non_whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with non-whitelisted address on behalf of a whitelisted, signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with non-whitelisted address on behalf of a whitelisted, non-signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address2)
#fails("Buys with non-whitelisted address on behalf of a non-whitelisted, signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, non_whitelisted_address2, 0, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address2) == balance
#
#balance = token.balance_of(non_whitelisted_address2)
#fails("Buys with non-whitelisted address on behalf of a non-whitelisted, non-signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, non_whitelisted_address2, 0, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address2) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys on behalf of themself with a whitelisted, signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address1, whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys on behalf of themself with a whitelisted, non-signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(whitelisted_address1, whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys on behalf of themself with a non-whitelisted, signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, non_whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys on behalf of themself with a non-whitelisted, non-signed and with invalid customerId address with buyOnBehalfWithSignedAddress.",
#  crowdsale.buy_on_behalf_with_signed_address(non_whitelisted_address1, non_whitelisted_address1, 0, v, r, s, 2))
#assert token.balance_of(non_whitelisted_address1) == balance



balance = token.balance_of(whitelisted_address1)
succeeds("Buys with whitelisted address and valid customerId with buyWithCustomerId.",
  crowdsale.buy_with_customer_id(1, whitelisted_address1, 2))
assert token.balance_of(whitelisted_address1) > balance

balance = token.balance_of(whitelisted_address1)
fails("Buys with whitelisted address and invalid customerId with buyWithCustomerId.",
  crowdsale.buy_with_customer_id(0, whitelisted_address1, 2))
assert token.balance_of(whitelisted_address1) == balance

balance = token.balance_of(non_whitelisted_address1)
succeeds("Buys with non-whitelisted address and valid customerId with buyWithCustomerId.",
  crowdsale.buy_with_customer_id(1, non_whitelisted_address1, 2))
assert token.balance_of(non_whitelisted_address1) > balance

balance = token.balance_of(non_whitelisted_address1)
fails("Buys with non-whitelisted address and invalid customerId with buyWithCustomerId.",
  crowdsale.buy_with_customer_id(0, non_whitelisted_address1, 2))
assert token.balance_of(non_whitelisted_address1) == balance



#balance = token.balance_of(whitelisted_address1)
#succeeds("Buys with whitelisted and signed address and valid customerId with buyWithSignedAddress",
#  crowdsale.buy_with_signed_address(1, v, r, s, whitelisted_address1, 2))
#assert token.balance_of(whitelisted_address1) > balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with whitelisted and signed address and invalid customerId with buyWithSignedAddress",
#  crowdsale.buy_with_signed_address(0, v, r, s, whitelisted_address1, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with whitelisted and unsigned address and valid customerId with buyWithSignedAddress",
#  crowdsale.buy_with_signed_address(1, v, r, s, whitelisted_address1, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(whitelisted_address1)
#fails("Buys with whitelisted and unsigned address and invalid customerId with buyWithSignedAddress",
#  crowdsale.buy_with_signed_address(0, v, r, s, whitelisted_address1, 2))
#assert token.balance_of(whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys with non-whitelisted and signed address and valid customerId with buyWithSignedAddress",
#  crowdsale.buy_with_signed_address(1, v, r, s, non_whitelisted_address1, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys with non-whitelisted and signed address and invalid customerId with buyWithSignedAddress",
#  crowdsale.buy_with_signed_address(0, v, r, s, non_whitelisted_address1, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys with non-whitelisted and unsigned address and valid customerId with buyWithSignedAddress",
#  crowdsale.buy_with_signed_address(1, v, r, s, non_whitelisted_address1, 2))
#assert token.balance_of(non_whitelisted_address1) == balance
#
#balance = token.balance_of(non_whitelisted_address1)
#fails("Buys with non-whitelisted and unsigned address and invalid customerId with buyWithSignedAddress",
#  crowdsale.buy_with_signed_address(0, v, r, s, non_whitelisted_address1, 2))
#assert token.balance_of(non_whitelisted_address1) == balance



balance = token.balance_of(non_whitelisted_address1)
succeeds("Preallocate tokens with non-whitelisted address",
  crowdsale.preallocate(non_whitelisted_address1, tokens_to_preallocate, 350))
assert token.balance_of(non_whitelisted_address1) > balance
assert token.balance_of(non_whitelisted_address1) == balance + (tokens_to_preallocate * (10 ** 18))

balance = token.balance_of(whitelisted_address2)
succeeds("Preallocate tokens with whitelisted address",
  crowdsale.preallocate(whitelisted_address2, tokens_to_preallocate, 350))
assert token.balance_of(whitelisted_address2) > balance
assert token.balance_of(whitelisted_address2) == balance + (tokens_to_preallocate * (10 ** 18))



crowdsale.end_ico()
assert states['Success'] == crowdsale.get_state(), "State should be Success"
print("CHAU ICO!")



succeeds("Finalize Crowdsale", crowdsale.finalize())
assert crowdsale.finalized() == True



miner.stop()