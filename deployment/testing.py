#!/usr/bin/python3 -i

import time

gas = 50000000
gas_price = 20000000000
web3 = None
miner = None
token_contract = None
crowdsale_contract = None
accounts = None
params = None

# Custom functions-------------------------------------------------------------------------
def add_token_address():
	token_contract.address = token()
	print("Token Address Added: " + token_contract.address)

def balances():
	for x in web3.eth.accounts:
		print(balance_of(x))

def get_transaction_receipt(tx_hash):
	status_deploy_crowdsale = status(tx_hash)
	if status_deploy_crowdsale == 1:
		return web3.eth.getTransactionReceipt(tx_hash)

def status(tx_receipt):
	wait()
	return web3.eth.getTransactionReceipt(tx_receipt).status

# Transaction parameter
def transaction_info(sender, value=0):
	return {"from": sender, "value": value*(10**18), "gas": gas, "gasPrice": gas_price}

def wait():
	block_number = web3.eth.blockNumber
	while web3.eth.blockNumber <= (block_number + 4):
		time.sleep(1)

# Crowdsale Contract's functions-----------------------------------------------------------
def buy(buyer, value):
	return status(crowdsale_contract.functions.buy().transact(transaction_info(buyer, value)))

def buy_on_behalf(receiver, value):
	pass

def buy_on_behalf_with_customer_id():
	pass

def buy_on_behalf_with_signed_address():
	pass

def buy_with_customer_id():
	pass

def buy_with_signed_address():
	pass

def configuration_crowdsale(params):
	hash_configured_transact = crowdsale_contract.functions.configurationCrowdsale(params[0], params[1], params[2], params[3], params[4]).transact(transaction_info(accounts[0]))
	print("\ntx hash: " + hash_configured_transact.hex() + "\n")
	return status(hash_configured_transact)

def configured():
	pass

def early_participant_whitelist():
	pass

def enable_lost_and_found_crowdsale():
	pass

def ends_at():
	pass

def finalize():
	new_ending = int(time.time()) + 5
	print(status(crowdsale_contract.functions.setEndingTime(new_ending).transact(transaction_info(accounts[0]))))
	time.sleep(2)
	print(status(crowdsale_contract.functions.finalize().transact(transaction_info(accounts[0]))))

def finalized():
	pass

def get_deployment_block():
	pass

def get_state():
	return crowdsale_contract.functions.getState().call()

def get_tranches_length():
	pass

def halt():
	pass

def halted():
	pass

def invested_amount_of():
	pass

def investor_count():
	pass

def multisig_wallet():
	pass

def owner():
	pass

def preallocate():
	pass

def require_customer_id():
	pass

def required_signed_address():
	pass

def set_early_participant_whitelist():
	pass

def set_require_customer_id():
	pass

def set_require_signed_address():
	pass

def signer_address():
	pass

def starts_at():
	pass

def token():
	print("Crowdsale instance in testing is None? " + str(crowdsale_contract == None))
	return crowdsale_contract.functions.token().call()

def token_amount_of():
	pass

def tokens_sold():
	pass

def tranches():
	pass

def transfer_ownership():
	pass

def unhalt():
	pass

def wei_raised():
	pass


# Token Contract's functions---------------------------------------------------------------

def add_approval():
	pass

def allowance():
	pass

def approve():
	pass

def balance_of(investor):
	if isinstance(investor, str):
		return token_contract.functions.balanceOf(investor).call()
	else:
		return token_contract.functions.balanceOf(web3.eth.accounts[investor]).call()

def can_upgrade():
	pass

def change_upgrade_master():
	pass

def decimals():
	pass

def enable_lost_and_found_token():
	pass

def get_upgrade_state():
	pass






















