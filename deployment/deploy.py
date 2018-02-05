#!/usr/bin/python3 -i
import web3
from web3 import Web3, IPCProvider
import json
import time
import os, errno
from datetime import datetime
from config import config_f
from address import generate_contract_address

ipcPath = '/home/coinfabrik/Programming/blockchain/node/geth.ipc'
web3 = Web3(IPCProvider(ipcPath))

tokenRetrieverAccount = "0x0F048ff7dE76B83fDC14912246AC4da5FA755cFE"
receipt = None
senderAccount = web3.eth.accounts[0]
gas = 50000000
gasPrice = 20000000000

def transactionInfo(value=0):
	return {"from": senderAccount, "value": value*(10**18), "gas": gas, "gasPrice": gasPrice}

def writeToJSONFile(path, fileName, data):
		filePathNameWExt = path + '/' + fileName + '.json'
		with open(filePathNameWExt, 'w') as fp:
			json.dump(data, fp, sort_keys=True, indent=4)

config = config_f('privateTestnet')
params = [config['multisig_owners'][0], config['startTime'], config['endTime'], tokenRetrieverAccount]
paramsLogPath = "./paramsLog"
buildPath = "./build"
config['tokenRetrieverAccount'] = tokenRetrieverAccount

try:
	if not os.path.exists(buildPath):
		os.makedirs(buildPath)
except OSError as e:
	if e.errno != errno.EEXIST:
		raise

with open("./build/Crowdsale.abi") as contract_abi_file:
	abi = json.load(contract_abi_file)

with open("./build/Crowdsale.bin") as contract_bin_file:
	bytecode = '0x' + contract_bin_file.read()


print("\nWeb3 version:", web3.version.api)

print(
  "\n\nMultisig address:", config['multisig_owners'][0], 
  "\n\nStart time:", time.ctime(config['startTime']),
  "\n\nEnd time:", time.ctime(config['endTime']),
  "\n\nToken retriever: " + tokenRetrieverAccount + "\n"
);

for x in range(0,int((len(config['tranches'])/4)-1)):
	print("Tranche #", x, " -----------------------------------------------------------------",
    "\nFullTokens cap:", int(config['tranches'][4*x]/(10**18)),
    "\nStart:         ", time.ctime(config['tranches'][4*x+1]),
    "\nEnd:           ", time.ctime(config['tranches'][4*x+2]),
    "\nTokens per EUR:", config['tranches'][4*x+3]
  )

print("------------------------------------------------------------------------------");
print("\nTransaction sender: " + senderAccount,
      "\n Gas and Gas price: " + str(gas) + " and " + str(gasPrice) + "\n"
)


invalidInput = True
consent = None

while invalidInput:

	consent = input('\nDo you agree with the information? [yes/no]: ')

	if(consent == 'yes' or consent == 'no'):
		invalidInput = False
	else:
		print("\nPlease enter 'yes' or 'no'\n")

deployName = input('\nEnter name of deployment: ')

localTime = datetime.now()

jsonFileName = "Crowdsale" + '-' + localTime.strftime('%Y-%m-%d--%H-%M-%S') + '--' + deployName

try:
	if not os.path.exists(paramsLogPath):
		os.makedirs(paramsLogPath)
except OSError as e:
	if e.errno != errno.EEXIST:
		raise

writeToJSONFile(paramsLogPath, jsonFileName, config)

crowdsale_contract = web3.eth.contract(abi=abi)
crowdsale_contract.bytecode = bytecode

nonce = web3.eth.getTransactionCount(senderAccount)
addressAttempt = generate_contract_address(senderAccount, nonce)

txHash = crowdsale_contract.deploy(transaction=transactionInfo(0), args=params)

print("\nContract address: " + addressAttempt + "\n")

time.sleep(15)

receipt = web3.eth.getTransactionReceipt(txHash)
crowdsale_contract.address = receipt.contractAddress