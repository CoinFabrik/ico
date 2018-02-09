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
secondAccount = web3.eth.accounts[1]
gas = 50000000
gasPrice = 20000000000

config = config_f('privateTestnet')
config['tokenRetrieverAccount'] = tokenRetrieverAccount
params = [config['multisig_owners'][0], config['startTime'], config['endTime'], config['tokenRetrieverAccount'], config['tranches']]
paramsLogPath = "./paramsLog"
buildPath = "./build"

pendingInput = True
consent = None


def transactionInfo(from_index=0, value=0):
	return {"from": web3.eth.accounts[from_index], "value": value*(10**18), "gas": gas, "gasPrice": gasPrice}

def writeToJSONFile(path, fileName, data):
	filePathNameWExt = path + '/' + fileName + '.json'
	with open(filePathNameWExt, 'w') as fp:
		json.dump(data, fp, sort_keys=True, indent=4)

try:
	if not os.path.exists(buildPath):
		os.makedirs(buildPath)
except OSError as e:
	if e.errno != errno.EEXIST:
		raise

with open("./build/Crowdsale.abi") as contract_abi_file:
	crowdsale_abi = json.load(contract_abi_file)

with open("./build/Crowdsale.bin") as contract_bin_file:
	crowdsale_bytecode = '0x' + contract_bin_file.read()

with open("./build/CrowdsaleToken.abi") as token_abi_file:
	token_abi = json.load(token_abi_file)

with open("./build/Crowdsale.bin") as contract_bin_file:
	token_bytecode = '0x' + contract_bin_file.read()


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
print("\n\nTransaction sender: " + senderAccount,
      "\nGas and Gas price: " + str(gas) + " and " + str(gasPrice) + "\n"
)


while pendingInput:

	consent = input('\nDo you agree with the information? [yes/no]: ')

	if(consent == 'yes' or consent == 'no'):
		pendingInput = False
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

writeToJSONFile(paramsLogPath, jsonFileName, config)


nonceCrowdsale = web3.eth.getTransactionCount(senderAccount)
generatedAddressCrowdsale = generate_contract_address(senderAccount, nonceCrowdsale)

crowdsale_contract = web3.eth.contract(address=generatedAddressCrowdsale, abi=crowdsale_abi, bytecode=token_bytecode)

txHashCrowdsale = crowdsale_contract.deploy(transaction=transactionInfo(0), args=None)

print("\n\nCrowdsale address: " + generatedAddressCrowdsale)


time.sleep(2)


nonceToken = web3.eth.getTransactionCount(senderAccount)
generatedAddressToken = generate_contract_address(senderAccount, nonceToken)

token_contract = web3.eth.contract(address=generatedAddressToken, abi=token_abi, bytecode=token_bytecode)

#txHashToken = crowdsale_contract.deploy(transaction=transactionInfo(0), args=None)

#print("\n\nCrowdsaleToken address: " + generatedAddressToken + "\n")


def configurateCall():
	hashConfiguredCall = crowdsale_contract.functions.configurationCrowdsale(params[0], params[1], params[2], params[3], params[4]).call(transactionInfo())

def configurateTransact():
	hashConfiguredTransact = crowdsale_contract.functions.configurationCrowdsale(params[0], params[1], params[2], params[3], params[4]).transact(transactionInfo())


def status(tx_receipt):
	time.sleep(2)
	return web3.eth.getTransactionReceipt(tx_receipt)["status"]

def addAddress():
	#receipt = eth.getTransactionReceipt(dHash)
	crowdsale_contract.address = generatedAddress
	print("Crowdsale:", contract.address)
	token_contract.address = token()
	print("Token:", token_contract.address)

def balance(investor):
	if isinstance(investor, str):
		return token_contract.balanceOf(investor).call(transactionInfo())
	else:
		return token_contract.balanceOf(web3.eth.accounts[investor]).call(transactionInfo())

def buy(buyer_index, value):
	return status(crowdsale_contract.buy().transact(transactionInfo(buyer_index, value)))

def end_now():
	new_ending = int(time.time()) + 5
	print(status(crowdsale_contract.setEndingTime(new_ending).transact(transactionInfo())))
	time.sleep(2)
	print(status(crowdsale_contract.finalize().transact(transactionInfo())))

def tokenCall():
	return contract.token().call()

def stateCall():
	return contract.getState().call()

def balances():
	for i in range(len(web3.eth.accounts)):
		print(balance(i))
