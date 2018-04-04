from web3_interface import Web3Interface

class Unlock:
  
  web3 = None
  
  def __init__(self):
    self.web3 = Web3Interface("middleware").w3
  
  def unlock(self):
    for x in self.web3.eth.accounts:
      self.web3.personal.unlockAccount(x, 'cuentahoracio0', 1800)