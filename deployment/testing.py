#!/usr/bin/python3 -i

import time

gas = 50000000
gasPrice = 20000000000
web3 = None
tokenContract = None
crowdsaleContract = None
firstAccount = None
secondAccount = None

# Transaction parameter
def transactionInfo(sender, value=0):
	return {"from": sender, "value": value*(10**18), "gas": gas, "gasPrice": gasPrice}

def wait():
	blockNum = web3.eth.blockNumber
	while web3.eth.blockNumber <= (blockNum + 2):
		time.sleep(1)

def status(tx_receipt):
	wait()
	return web3.eth.getTransactionReceipt(tx_receipt).status

def crowdsaleReceipt(tx_hash):
    statusDeployCrowdsale = status(tx_hash)
    if statusDeployCrowdsale == 1:
    	return web3.eth.getTransactionReceipt(tx_hash)

def configurate(params):
	hashConfiguredTransact = crowdsaleContract.functions.configurationCrowdsale(params[0], params[1], params[2], params[3], params[4]).transact(transactionInfo(firstAccount))
	print("\ntx hash: " + hashConfiguredTransact.hex() + "\n")
	return status(hashConfiguredTransact)

def balance(investor):
	if isinstance(investor, str):
		return tokenContract.functions.balanceOf(investor).call(transactionInfo(firstAccount))
	else:
		return tokenContract.functions.balanceOf(web3.eth.accounts[investor]).call(transactionInfo(firstAccount))

def buy(buyer, value):
	return status(crowdsaleContract.functions.buy().transact(transactionInfo(buyer, value)))

def end_now():
	new_ending = int(time.time()) + 5
	print(status(crowdsaleContract.functions.setEndingTime(new_ending).transact(transactionInfo(firstAccount))))
	time.sleep(2)
	print(status(crowdsaleContract.functions.finalize().transact(transactionInfo(firstAccount))))

def token():
	return crowdsaleContract.functions.token().call()

def state():
	return crowdsaleContract.functions.getState().call()

def balances():
	for x in web3.eth.accounts:
		print(balance(x))

def addTokenAddress():
	tokenContract.address = token()
	print("Token Address Added: " + tokenContract.address)