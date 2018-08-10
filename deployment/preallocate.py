#!/usr/bin/env python3

import sys
import json
print(sys.version)
from web3 import Web3, HTTPProvider
from datetime import datetime

web3 = Web3(HTTPProvider('http://localhost:8545'))

contract_name = "Crowdsale"

with open("./build/" + contract_name + ".abi") as contract_abi_file:
  contract_abi = json.load(contract_abi_file)

crowdsale = web3.eth.contract(abi=contract_abi, address="0xDdAd02F008E310D2fED6546828Fc81769fe20978")

crowdsale.functions.preallocate("0x878d7ed5C194349F37b18688964E8db1EB0fcCa1", 300 * (10 ** 6), 0).transact({
  "from": "0x54d9249C776C56520A62faeCB87A00E105E8c9Dc",
  "gas": 200000,
  "gasPrice": web3.toWei(14, "gwei")
})
