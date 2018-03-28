#!/usr/bin/env python3

import sys
from deployer import deployer
from checker import fails, succeeds

http_provider = sys.argv[1]

web3 = Web3(HTTPProvider(http_provider))

tx = {'from': account,
  'to': self.contract.address,
  'value': value,
  'gas': 100000000
  }

deployer = Deployer(web3, )

haltable = deployer.deploy("Haltable")

assert haltable.functions.halted().call() == False

succeeds(haltable.functions.halt().transact(tx))

assert haltable.functions.halted().call() == True

succeeds(haltable.unhalt().call())

assert haltable.functions.halted().call() == False