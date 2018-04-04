#!/usr/bin/env python3

from web3_interface import Web3Interface
import json
from unlock import Unlock
import os, errno
from datetime import datetime
from deployer import Deployer

# web3.py instance
web3 = Web3Interface(middleware=True).w3
miner = web3.miner
unlocker = Unlock()
sender_account = web3.eth.accounts[0]
gas = 50000000
gas_price = 20000000000
address_log_path = "./address_log/"

# Unlock accounts
unlocker.unlock()

miner.start(1)

deployer = Deployer()

print("\nDeploying contract...")
(crowdsale_contract, receipt) = deployer.deploy("./build/", "Crowdsale", sender_account, {"from": sender_account, "value": 0, "gas": gas, "gasPrice": gas_price},)

print("\nDeployment successful: " + str(receipt.status == 1))

print("\nCrowdsale address: " + crowdsale_contract.address)

print("\nGas used: " + str(receipt.gasUsed) + "\n")


# Write json file with crowdsale contract's address into address_log folder -------------------------
if __name__ == "__main__":
  deployment_name = input('\n\nEnter name of deployment: ')
else:
  deployment_name = "test"

local_time = datetime.now()

json_file_name = "Crowdsale-Address" + '--' + local_time.strftime('%Y-%m-%d--%H-%M-%S') + '--' + deployment_name

try:
  if not os.path.exists(address_log_path):
    os.makedirs(address_log_path)
except OSError as e:
  if e.errno != errno.EEXIST:
    raise

# Writing configuration parameters into json file for logging purposes
file_path_name_w_ext = address_log_path + json_file_name + '.json'
address_for_file = {'crowdsale_address': crowdsale_contract.address}
with open(file_path_name_w_ext, 'w') as fp:
  json.dump(address_for_file, fp, sort_keys=True, indent=2)
# ------------------------------------------------------------------------------------------
