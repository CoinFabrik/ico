from web3 import Web3
from web3.middleware import geth_poa_middleware
from cli_args import args
import json

class Web3Interface:
  w3 = None
  def __init__(self):
    provider_param = None
    with open("../deployment/networks.json") as networks_file:
      networks = json.load(networks_file)
    if args.provider == "ipc":
      provider_param = networks[args.network][args.provider]["path"]
      self.w3 = Web3(Web3.IPCProvider(provider_param))
    elif args.provider == "ws":
      provider_param = args.provider + "://" + networks[args.network][args.provider]["host"] + ":" + str(networks[args.network][args.provider]["port"])
      self.w3 = Web3(Web3.WebsocketProvider(provider_param))
    elif args.provider == "http":
      provider_param = args.provider + "://" + networks[args.network][args.provider]["host"] + ":" + str(networks[args.network][args.provider]["port"])
      self.w3 = Web3(Web3.HTTPProvider(provider_param))
    else:
      raise ValueError("Provider not within the admitted options.")
    if (args.network == "poanet"):
      self.w3.middleware_stack.inject(geth_poa_middleware, layer=0)