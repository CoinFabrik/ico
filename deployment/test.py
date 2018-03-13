#!/usr/bin/python3 -i

import deploy
import setConfig
from testing_helpers import Crowdsale, Token


# Assign configuration function to local variable
configurate = setConfig.configurate

# Dict with the states for comparison
states = {"Unknown": 0, "PendingConfiguration": 1, "PreFunding": 2, "Funding": 3, "Success": 4, "Finalized": 5}

addressZero = '0x0000000000000000000000000000000000000000'


# Testing start

# Pre-configuration testing

crowdsale = Crowdsale(deploy.crowdsale_contract.address)


# Configuration
(token_address2, token_contract2) = configurate()

crowdsale.buy(crowdsale.accounts[1], 1000)

setConfig.wait()

token = Token(crowdsale.contract)

state = crowdsale.getState()

print(state == states["Unknown"])

print(state == states["PendingConfiguration"])

print(state == states["PreFunding"])

print(state == states["Funding"])

print(state == states["Success"])

print(state == states["Finalized"])

assert token.balance_of(token.accounts[1]) > 0

# Post-configuration testing



deploy.miner.stop()