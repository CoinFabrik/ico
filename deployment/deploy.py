#!/usr/bin/python3 -i

import sys
from web3 import Web3, IPCProvider
import json
from address import generate_contract_address
import unlock
import os, errno
import time
from datetime import datetime

# Change ipc_path if needed
ipc_path = '/home/coinfabrik/Programming/blockchain/node/geth.ipc'
# web3.py instance
web3 = Web3(IPCProvider(ipc_path))
miner = web3.miner

accounts = web3.eth.accounts
sender_account = accounts[0]
gas = 50000000
gas_price = 20000000000
address_log_path = "./address_log"
unlock.web3 = web3

# Get Crowdsale ABI
with open("./build/Crowdsale.abi") as contract_abi_file:
	crowdsale_abi = json.load(contract_abi_file)

# Get Crowdsale Bytecode
with open("./build/Crowdsale.bin") as contract_bin_file:
	crowdsale_bytecode = '0x' + contract_bin_file.read()

nonce_crowdsale = web3.eth.getTransactionCount(sender_account)
crowdsale_address = generate_contract_address(sender_account, nonce_crowdsale)

# Crowdsale instance creation
crowdsale_contract = web3.eth.contract(address=crowdsale_address, abi=crowdsale_abi, bytecode=crowdsale_bytecode)

# Unlock accounts
unlock.unlock()

miner.start(1)

# Crowdsale contract deployment
tx_hash_crowdsale = crowdsale_contract.deploy(transaction={"from": sender_account, "value": 0, "gas": gas, "gasPrice": gas_price}, args=None)

print("\n\nCrowdsale address: " + crowdsale_address + "\n")

block_number = web3.eth.blockNumber
while web3.eth.blockNumber <= (block_number + 1):
	time.sleep(1)


# Write json file with crowdsale contract's address into address_log folder -------------------------
if __name__ == "__main__":
	deployment_name = input('\n\nEnter name of deployment: ')
else:
	deployment_name = "test"

local_time = datetime.now()

json_file_name = "Crowdsale-Address" + '--' + local_time.strftime('%Y-%m-%d--%H-%M-%S') + '--' + deployment_name

try:
	if not os.path.exists(address_log_path):
		os.makedirs(address_log_path)
except OSError as e:
	if e.errno != errno.EEXIST:
		raise

# Writing configuration parameters into json file for logging purposes
file_path_name_w_ext = address_log_path + '/' + json_file_name + '.json'
address_for_file = {'crowdsale_address': crowdsale_address}
with open(file_path_name_w_ext, 'w') as fp:
	json.dump(address_for_file, fp, sort_keys=True, indent=2)
# ------------------------------------------------------------------------------------------
