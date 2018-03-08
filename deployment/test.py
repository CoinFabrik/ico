#!/usr/bin/python3 -i

import deploy
import setConfig
import testing_helpers

#Assigning testing module functions and variables to local variables
transaction_info = testing_helpers.transaction_info
wait = testing_helpers.wait
status = testing_helpers.status
get_transaction_receipt = testing_helpers.get_transaction_receipt
balance_of = testing_helpers.balance_of
buy = testing_helpers.buy
finalize = testing_helpers.finalize
token = testing_helpers.token
get_state = testing_helpers.get_state
balances = testing_helpers.balances
add_token_address = testing_helpers.add_token_address

configurate = setConfig.configurate

miner = deploy.miner

miner.stop()