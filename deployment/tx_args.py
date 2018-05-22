from web3 import Web3

def tx_args(sender, gas=200000, gasPrice=9000000000, value=0):
  return {"from": sender, "value": Web3.toWei(value, "ether"), "gas": gas, "gasPrice": gasPrice}