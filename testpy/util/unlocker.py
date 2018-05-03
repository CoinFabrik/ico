from .web3_interface import Web3Interface

def unlock():
  web3 = Web3Interface().w3
  for x in web3.eth.accounts:
    web3.personal.unlockAccount(x, 'cuentahoracio0', 10000)