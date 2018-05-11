from web3 import Web3
from web3.middleware import geth_poa_middleware
import argparse
import json

class Web3Interface:
  w3 = None
  def __init__(self):
    provider_param = None
    parser = argparse.ArgumentParser()
    parser.add_argument("-n", "--network", default="poanet", help="Enter network, defaults to poanet")
    parser.add_argument("-p", "--provider", default="http", help="Enter provider, defaults to http")
    parser.add_argument("-a", "--address", help="Enter address to look for log file")
    parser.add_argument("-d", "--deployment_name", help="Enter deployment name to look for log file")
    parser.add_argument("-t", "--test", action="store_true", help="Testing mode")
    parser.add_argument("-c", "--configurate", action="store_true")
    args = parser.parse_args()
    with open("../deployment/networks.json") as networks_file:
      networks = json.load(networks_file)
    try:
      if args.provider == "ipc":
        provider_param = networks[args.network][args.provider]["path"]
        self.w3 = Web3(Web3.IPCProvider(provider_param))
      elif args.provider == "ws":
        provider_param = args.provider + "://" + networks[args.network][args.provider]["host"] + ":" + str(networks[args.network][args.provider]["port"])
        self.w3 = Web3(Web3.WebsocketProvider(provider_param))
      else:
        provider_param = args.provider + "://" + networks[args.network][args.provider]["host"] + ":" + str(networks[args.network][args.provider]["port"])
        self.w3 = Web3(Web3.HTTPProvider(provider_param))
    except IndexError:
      print("IndexError")
      pass
    if (args.network == "poanet"):
      self.w3.middleware_stack.inject(geth_poa_middleware, layer=0)