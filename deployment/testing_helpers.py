#!/usr/bin/python3 -i

import time
from web3 import Web3, IPCProvider
import json
import glob
import os

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

# Get Crowdsale ABI
with open("./build/Crowdsale.abi") as contract_abi_file:
	crowdsale_abi = json.load(contract_abi_file)

# Get Crowdsale Bytecode
with open("./build/Crowdsale.bin") as contract_bin_file:
	crowdsale_bytecode = '0x' + contract_bin_file.read()

file_list = glob.glob('./address_log/*')
latest_file = max(file_list, key=os.path.getctime)

# Get Crowdsale address
with open(latest_file) as contract_address_file:
	crowdsale_address_json = json.load(contract_address_file)

crowdsale_address = crowdsale_address_json['crowdsale_address']

# Crowdsale instance creation
crowdsale_contract = web3.eth.contract(address=crowdsale_address, abi=crowdsale_abi, bytecode=crowdsale_bytecode)

# Get CrowdsaleToken ABI
with open("./build/CrowdsaleToken.abi") as token_abi_file:
	token_abi = json.load(token_abi_file)

token_address = crowdsale_contract.functions.token().call()
token_contract = web3.eth.contract(address=token_address, abi=token_abi)


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
	return status(crowdsale_contract.functions.buyOnBehalf(receiver).transact(transaction_info(sender_account, value)))

def buy_on_behalf_with_customer_id(receiver, customerId, value):
	return status(crowdsale_contract.functions.buyOnBehalfWithCustomerId(receiver, customerId).transact(transaction_info(sender_account, value)))

def buy_on_behalf_with_signed_address(receiver, customerId, v, r, s, value):
	return status(crowdsale_contract.functions.buyOnBehalfWithSignedAddress(receiver, customerId, v, r, s).transact(transaction_info(sender_account, value)))

def buy_with_customer_id(customerId, value):
	return status(crowdsale_contract.functions.buyOnBehalfWithSignedAddress(customerId).transact(transaction_info(sender_account, value)))

def buy_with_signed_address(customerId, v, r, s, value):
	return status(crowdsale_contract.functions.buyWithSignedAddress(customerId, v, r, s).transact(transaction_info(sender_account, value)))

# Implemented in setConfig module
#def configuration_crowdsale(params):
#	hash_configured_transact = crowdsale_contract.functions.configurationCrowdsale(params[0], params[1], params[2], params[3], params[4]).transact(transaction_info(accounts[0]))
#	print("\ntx hash: " + hash_configured_transact.hex() + "\n")
#	return status(hash_configured_transact)

def configured():
	return crowdsale_contract.functions.configured().call()

def early_participant_whitelist():
	return crowdsale_contract.functions.earlyParticipantWhitelist().call()

def ends_at():
	return crowdsale_contract.functions.endsAt().call()

def finalize():
	new_ending = int(time.time()) + 5
	print(status(crowdsale_contract.functions.setEndingTime(new_ending).transact(transaction_info(accounts[0]))))
	time.sleep(2)
	print(status(crowdsale_contract.functions.finalize().transact(transaction_info(accounts[0]))))

def finalized():
	return crowdsale_contract.functions.finalized().call()

def get_deployment_block():
	return crowdsale_contract.functions.getDeploymentBlock().call()

def get_state():
	return crowdsale_contract.functions.getState().call()

def get_tranches_length():
	return crowdsale_contract.functions.getTranchesLength().call()

def halt():
	return status(crowdsale_contract.functions.halt().transact(transaction_info(sender_account)))

def halted():
	return crowdsale_contract.functions.halted().call()

def invested_amount_of():
	pass

def investor_count():
	pass

def multisig_wallet():
	return crowdsale_contract.functions.multisigWallet().call()

def owner():
	return crowdsale_contract.functions.owner().call()

def preallocate():
	pass

def require_customer_id():
	return crowdsale_contract.functions.requireCustomerId().call()

def required_signed_address():
	return crowdsale_contract.functions.requiredSignedAddress().call()

def set_early_participant_whitelist(addr, status):
	return status(crowdsale_contract.functions.setEarlyParticipantWhitelist(addr, status).transact(transaction_info(sender_account)))

def set_require_customer_id(value):
	return status(crowdsale_contract.functions.setRequireCustomerId(value).transact(transaction_info(sender_account)))

def set_require_signed_address(value, signer):
	return status(crowdsale_contract.functions.setRequireSignedAddress(value, signer).transact(transaction_info(sender_account)))

def signer_address():
	return crowdsale_contract.functions.signerAddress().call()

def starts_at():
	return crowdsale_contract.functions.startsAt().call()

def token():
	return crowdsale_contract.functions.token().call()

def token_amount_of():
	return crowdsale_contract.functions.tokenAmountOf().call()

def tokens_sold():
	return crowdsale_contract.functions.tokensSold().call()

def tranches():
	return crowdsale_contract.functions.tranches().call()

def transfer_ownership(newOwner):
	return status(crowdsale_contract.functions.transferOwnership(newOwner).transact(transaction_info(sender_account)))

def unhalt():
	return status(crowdsale_contract.functions.unhalt().transact(transaction_info(sender_account)))

def wei_raised():
	return crowdsale_contract.functions.weiRaised().call()


# Token Contract's functions---------------------------------------------------------------
def add_approval(spender, addedValue):
	return token_contract.functions.addApproval(spender, addedValue).transact(transaction_info(sender_account))

def allowance(account, spender):
	return token_contract.functions.allowance(account, spender).call()

def approve(spender, value):
	return token_contract.functions.approve(spender, value).transact(transaction_info(sender_account))

def balance_of(investor):
	if isinstance(investor, str):
		return token_contract.functions.balanceOf(investor).call()
	else:
		return token_contract.functions.balanceOf(web3.eth.accounts[investor]).call()

def can_upgrade():
	return token_contract.functions.canUpgrade().call()

def change_upgrade_master(newMaster):
	return token_contract.functions.changeUpgradeMaster(newMaster).transact(transaction_info(sender_account))

def decimals():
	return token_contract.functions.decimals().call()

def enable_lost_and_found(agent, tokens, token_contr):
	return token_contract.functions.enableLostAndFound(agent, tokens, token_contr).transact(transaction_info(sender_account))

def get_upgrade_state():
	return token_contract.functions.getUpgradeState().call()

def sub_approval(spender, subtractedValue):
	return token_contract.functions.subApproval(spender, subtractedValue).transact(transaction_info(sender_account))

def total_supply():
	return token_contract.functions.totalSupply().call()

def transfer(to, value):
	return token_contract.functions.transfer(to, value).transact(transaction_info(sender_account))

def transferFrom(from_addr, to, value):
	return token_contract.functions.transferFrom(from_addr, to, value).transact(transaction_info(sender_account))