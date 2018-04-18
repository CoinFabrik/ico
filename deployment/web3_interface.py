from web3 import Web3
from web3.middleware import geth_poa_middleware
import argparse
import json

class Web3Interface:
  parser = argparse.ArgumentParser()
  parser.add_argument("-n", "--network", default="poanet")
  parser.add_argument("-p", "--provider", default="http")
  parser.add_argument("-t", "--test", action="store_true")
  args = parser.parse_args()
  
  with open("networks.json") as networks_file:
    networks = json.load(networks_file)

  provider_param = None
  w3 = None
  ip = None
  port = None

  def __init__(self):
    try:
      if self.args.provider == "ipc":
        self.provider_param = self.networks[self.args.network][self.args.provider]["path"]
        self.w3 = Web3(Web3.IPCProvider(self.provider_param))
      elif self.args.provider == "ws":
        self.provider_param = self.args.provider + "://" + self.networks[self.args.network][self.args.provider]["host"] + ":" + str(self.networks[self.args.network][self.args.provider]["port"])
        self.w3 = Web3(Web3.WebsocketProvider(self.provider_param))
      else:
        self.provider_param = self.args.provider + "://" + self.networks[self.args.network][self.args.provider]["host"] + ":" + str(self.networks[self.args.network][self.args.provider]["port"])
        self.w3 = Web3(Web3.HTTPProvider(self.provider_param))
    except IndexError:
      print("IndexError")
      pass

    if (args.network == "poanet"):
      self.w3.middleware_stack.inject(geth_poa_middleware, layer=0)
