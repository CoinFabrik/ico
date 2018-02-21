#!/usr/bin/python3 -i

import sys

print(sys.argv)

if len(sys.argv) == 1:
	from config import config_f
elif sys.argv[1] == 'test':
	from configTest import config_t as config_f
else:
	sys.exit("Unknown argument: " + sys.argv[1])

from web3 import Web3, IPCProvider
import json
import time
import os, errno
from datetime import datetime
from address import generate_contract_address
import testing
import unlock

# Change ipcPath if needed
ipcPath = '/home/coinfabrik/Programming/blockchain/node/geth.ipc'
# web3.py instance
web3 = Web3(IPCProvider(ipcPath))

miner = web3.miner

unlock.web3 = web3
testing.web3 = web3

tokenRetrieverAccount = "0x0F048ff7dE76B83fDC14912246AC4da5FA755cFE"
firstAccount = web3.eth.accounts[0]
secondAccount = web3.eth.accounts[1]
testing.firstAccount = firstAccount
testing.secondAccount = secondAccount
gas = 50000000
gasPrice = 20000000000


# Dict of configuration parameters
config = config_f('privateTestnet')
config['tokenRetrieverAccount'] = tokenRetrieverAccount
params = [config['multisig_owners'][0], config['startTime'], config['endTime'], config['tokenRetrieverAccount'], config['tranches']]
paramsLogPath = "./paramsLog"
buildPath = "./build"

# Get Crowdsale ABI
with open("./build/Crowdsale.abi") as contract_abi_file:
	crowdsale_abi = json.load(contract_abi_file)

# Get Crowdsale Bytecode
with open("./build/Crowdsale.bin") as contract_bin_file:
	crowdsale_bytecode = '0x' + contract_bin_file.read()

# Get CrowdsaleToken ABI
with open("./build/CrowdsaleToken.abi") as token_abi_file:
	token_abi = json.load(token_abi_file)


# Creates 'build' folder if it doesn't exist
try:
	if not os.path.exists(buildPath):
		os.makedirs(buildPath)
except OSError as e:
	if e.errno != errno.EEXIST:
		raise

def dump():
	
	pendingInput = True
	consent = None
	
	# Displaying configuration parameters ----------------------------------------------------------------------------------
	
	print("\n\nWeb3 version:", web3.version.api)
	
	print(
	  "\n\nMultisig address:", config['multisig_owners'][0], 
	  "\n\nStart time:", time.ctime(config['startTime']),
	  "\n\nEnd time:", time.ctime(config['endTime']),
	  "\n\nToken retriever: " + tokenRetrieverAccount
	);
	
	for x in range(0,int((len(config['tranches'])/4)-1)):
		print("\n\nTranche #", x, " -----------------------------------------------------------------",
	    "\nFullTokens cap:", int(config['tranches'][4*x]/(10**18)),
	    "\nStart:         ", time.ctime(config['tranches'][4*x+1]),
	    "\nEnd:           ", time.ctime(config['tranches'][4*x+2]),
	    "\nTokens per EUR:", config['tranches'][4*x+3]
	  )
	
	print("------------------------------------------------------------------------------");
	print("\n\nTransaction sender: " + firstAccount,
	      "\nGas and Gas price: " + str(gas) + " and " + str(gasPrice) + "\n"
	)
	
	# ----------------------------------------------------------------------------------------------------------------------
	
	# Validating configuration parameters
	
	while pendingInput:
	
		consent = input('\nDo you agree with the information? [yes/no]: ')
	
		if consent == 'yes':
			pendingInput = False
		elif consent == 'no':
			sys.exit("Aborted")
		else:
			print("\n\nPlease enter 'yes' or 'no'\n")
	
	deployName = input('\n\nEnter name of deployment: ')
	
	localTime = datetime.now()
	
	jsonFileName = "Crowdsale" + '-' + localTime.strftime('%Y-%m-%d--%H-%M-%S') + '--' + deployName
	
	try:
		if not os.path.exists(paramsLogPath):
			os.makedirs(paramsLogPath)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	
	# Writing configuration parameters into json file for logging purposes
	filePathNameWExt = paramsLogPath + '/' + jsonFileName + '.json'
	with open(filePathNameWExt, 'w') as fp:
		json.dump(config, fp, sort_keys=True, indent=4)


if len(sys.argv) == 1:
	dump()


nonceCrowdsale = web3.eth.getTransactionCount(firstAccount)
generatedAddressCrowdsale = generate_contract_address(firstAccount, nonceCrowdsale)

# Crowdsale instance creation
crowdsale_contract = web3.eth.contract(address=generatedAddressCrowdsale, abi=crowdsale_abi, bytecode=crowdsale_bytecode)

# Unlock accounts
unlock.unlock()

miner.start(1)

# Crowdsale contract deployment
txHashCrowdsale = crowdsale_contract.deploy(transaction=testing.transactionInfo(firstAccount), args=None)

print("\n\nCrowdsale address: " + generatedAddressCrowdsale + "\n")

receipt = testing.crowdsaleReceipt(txHashCrowdsale)

if receipt.status == 1:
	print("\nDeployment Status: Successful\n")
else:
	print("\nDeployment Status: Unsuccessful\n")

testing.crowdsaleContract = crowdsale_contract





testing.configurate(params)

testing.wait()

tokenAddress = crowdsale_contract.functions.token().call()

token_contract = web3.eth.contract(address=tokenAddress, abi=token_abi)
testing.tokenContract = token_contract

miner.stop()

print('Soy el final del archivo')