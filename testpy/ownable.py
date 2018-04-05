#!/usr/bin/env python3

from deployer import Deployer
from web3_interface import Web3Interface
from tx_checker import fails, succeeds

web3 = Web3Interface(middleware=True).w3

deployer = Deployer()

owner = web3.eth.accounts[0]
new_owner = web3.eth.accounts[1]
gas = 50000000
gas_price = 20000000000

(ownable, receipt) = deployer.deploy("./OwnerBuild/", "Ownable", owner, {"from": owner, "value": 0, "gas": gas, "gasPrice": gas_price},)

assert ownable.functions.owner().call() == owner

succeeds("Transfer ownership succeeds.", ownable.functions.transferOwnership(new_owner).transact({"from": owner, "value": 0, "gas": gas, "gasPrice": gas_price}))

assert ownable.functions.owner().call() == new_owner