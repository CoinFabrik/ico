from web3_interface import Web3Interface

web3 = Web3Interface().w3
def fails(message, tx_hash):
  print(message, end='')
  try:
    assert web3.eth.waitForTransactionReceipt(tx_hash).status == 0
  except Exception as e:
    print(" ✗✘")
    raise AssertionError("Transaction expected to fail succeeded")
  else:
    print(" ✓✔")

def succeeds(message, tx_hash):
  print(message, end='')
  try:
    assert web3.eth.waitForTransactionReceipt(tx_hash).status == 1
  except Exception as e:
    print(" ✗✘")
    raise AssertionError("Transaction expected to succeed failed")
  else:
    print(" ✓✔")