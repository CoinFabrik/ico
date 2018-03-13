#!/usr/bin/python3 -i

import sys
from datetime import datetime
import json
import time
import os, errno
import glob
import unlock
from web3 import Web3, IPCProvider

if __name__ == '__main__':
	from config import config_f
else:
	from configTest import config_t as config_f


# Dict of configuration parameters
token_retriever_account = "0x0F048ff7dE76B83fDC14912246AC4da5FA755cFE"
config = config_f('privateTestnet')
config['token_retriever_account'] = token_retriever_account
params = [config['multisig_owners'][0], config['startTime'], config['endTime'], config['token_retriever_account'], config['tranches'], 1, 15, 525 * (10 ** 5) * (10 ** 15)]
params_log_path = "./params_log"

# Change ipcPath if needed
ipc_path = '/home/coinfabrik/Programming/blockchain/node/geth.ipc'
# web3.py instance
web3 = Web3(IPCProvider(ipc_path))
miner = web3.miner
accounts = web3.eth.accounts
sender_account = accounts[0]
gas = 50000000
gas_price = 20000000000
unlock.web3 = web3
unlock.unlock()

# Get Crowdsale ABI
with open("./build/Crowdsale.abi") as contract_abi_file:
	crowdsale_abi = json.load(contract_abi_file)

# Get Crowdsale Bytecode
with open("./build/Crowdsale.bin") as contract_bin_file:
	crowdsale_bytecode = '0x' + contract_bin_file.read()

file_list = glob.glob('./address_log/*')
latest_file = max(file_list, key=os.path.getctime)

# Get Syndicatev2 address
with open(latest_file) as contract_address_file:
	crowdsale_address_json = json.load(contract_address_file)

crowdsale_address = crowdsale_address_json['crowdsale_address']

# Crowdsale instance creation
crowdsale_contract = web3.eth.contract(address=crowdsale_address, abi=crowdsale_abi, bytecode=crowdsale_bytecode)


# Get CrowdsaleToken ABI
with open("./build/CrowdsaleToken.abi") as token_abi_file:
	token_abi = json.load(token_abi_file)

def wait():
	block_number = web3.eth.blockNumber
	while web3.eth.blockNumber <= (block_number + 1):
		time.sleep(1)

# Display configuration parameters, confirm them, write them to json file
def dump():
	
	pending_input = True
	consent = None
	
	# Displaying configuration parameters ----------------------------------------------------------------------------------
	print("\n\nWeb3 version:", web3.version.api)
	
	print(
	  "\n\nMultisig address:", config['multisig_owners'][0], 
	  "\n\nStart time:", time.ctime(config['startTime']),
	  "\n\nEnd time:", time.ctime(config['endTime']),
	  "\n\nToken retriever: " + config['token_retriever_account']
	);
	
	for x in range(0,int((len(config['tranches'])/4)-1)):
		print("\n\nTranche #", x, " -----------------------------------------------------------------",
	    "\nFullTokens cap:", int(config['tranches'][4*x]/(10**18)),
	    "\nStart:         ", time.ctime(config['tranches'][4*x+1]),
	    "\nEnd:           ", time.ctime(config['tranches'][4*x+2]),
	    "\nTokens per EUR:", config['tranches'][4*x+3]
	  )
	
	print("------------------------------------------------------------------------------");
	print("\n\nTransaction sender: " + accounts[0],
	      "\nGas and Gas price: " + str(gas) + " and " + str(gas_price) + "\n"
	)
	
	# ----------------------------------------------------------------------------------------------------------------------
	
	# Validating configuration parameters
	while pending_input:
	
		consent = input('\nDo you agree with the information? [yes/no]: ')
	
		if consent == 'yes':
			pending_input = False
		elif consent == 'no':
			sys.exit("Aborted")
		else:
			print("\n\nPlease enter 'yes' or 'no'\n")
	
	deployment_name = input('\n\nEnter name of deployment: ')
	
	local_time = datetime.now()
	
	json_file_name = "Crowdsale" + '-' + local_time.strftime('%Y-%m-%d--%H-%M-%S') + '--' + deployment_name
	
	try:
		if not os.path.exists(params_log_path):
			os.makedirs(params_log_path)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	
	# Writing configuration parameters into json file for logging purposes
	file_path_name_w_ext = params_log_path + '/' + json_file_name + '.json'
	with open(file_path_name_w_ext, 'w') as fp:
		json.dump(config, fp, sort_keys=True, indent=2)

if __name__ == '__main__':
	print("\n\nEnter 'configurate()' to configurate Crowdsale. Returns (token_address, token_contract) tuple.")

def configurate():
	if __name__ == '__main__':
		dump()
	miner.start(1)
	hash_configured_transact = crowdsale_contract.functions.configurationCrowdsale(params[0], params[1], params[2], params[3], params[4], params[5], params[6], params[7]).transact({"from": sender_account, "value": 0, "gas": gas, "gasPrice": gas_price})
	print("\n\nConfiguration Tx Hash: " + hash_configured_transact.hex() + "\n")
	wait()
	print(web3.eth.getTransactionReceipt(hash_configured_transact))
	token_address = crowdsale_contract.functions.token().call()
	token_contract = web3.eth.contract(address=token_address, abi=token_abi)
	return (token_address, token_contract)
