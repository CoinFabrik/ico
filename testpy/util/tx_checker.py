def fails(message, tx_receipt):
  print(message, end='')
  try:
    assert tx_receipt.status == 0
  except Exception as e:
    print(" ✗✘")
    raise "Transaction expected to fail succeeded"
  else:
    print(" ✓✔")

def succeeds(message, tx_receipt):
  print(message, end='')
  try:
    assert tx_receipt.status == 1
  except Exception as e:
    print(" ✗✘")
    raise "Transaction expected to succeed failed"
  else:
    print(" ✓✔")