from .web3_interface import Web3Interface

class Unlocker:
  
  web3 = None
  
  def __init__(self):
    self.web3 = Web3Interface().w3
  
  def unlock(self):
    for x in self.web3.eth.accounts:
      self.web3.personal.unlockAccount(x, 'cuentahoracio0', 90000)