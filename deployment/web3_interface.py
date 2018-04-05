from web3 import Web3, IPCProvider
from web3.middleware import geth_poa_middleware

class Web3Interface:
  
  ipc_path = None
  w3 = None

  def __init__(self, middleware=False):
    # Change ipc_path if needed
    self.ipc_path = '/home/coinfabrik/Programming/blockchain/node/geth.ipc'
    # web3.py instance
    self.w3 = Web3(IPCProvider(self.ipc_path))
    # self.w3 = Web3(HTTPProvider("http://localhost:8545"))
    if middleware:
      self.w3.middleware_stack.inject(geth_poa_middleware, layer=0)