def test_haltable(chain):
  haltable, _ = chain.provider.get_or_deploy_contract('Haltable')

  halted = haltable.call().halted()
  assert halted == False


def test_it_does_halt(chain):
  haltable, _ = chain.provider.get_or_deploy_contract('Haltable')

  set_txn_hash = haltable.transact().halt()
  chain.wait.for_receipt(set_txn_hash)

  halted = haltable.call().halted()
  assert halted == True 

def test_it_does_not_halt(chain):
  haltable, _ = chain.provider.get_or_deploy_contract('Haltable')

  try:
    set_txn_hash = haltable.transact({'from': chain.web3.eth.accounts[1]}).halt()
    chain.wait.for_receipt(set_txn_hash)
    pass
  except Exception as e:
    pass

  halted = haltable.call().halted()
  assert halted == False 


def test_it_does_unhalt(chain):
  haltable, _ = chain.provider.get_or_deploy_contract('Haltable')

  set_txn_hash = haltable.transact().halt()
  chain.wait.for_receipt(set_txn_hash)

  halted = haltable.call().halted()
  assert halted == True 

  set_txn_hash = haltable.transact().unhalt()
  chain.wait.for_receipt(set_txn_hash)

  halted = haltable.call().halted()
  assert halted == False 

def test_it_does_not_unhalt(chain):
  haltable, _ = chain.provider.get_or_deploy_contract('Haltable')

  set_txn_hash = haltable.transact().halt()
  chain.wait.for_receipt(set_txn_hash)

  halted = haltable.call().halted()
  assert halted == True 

  try:
    set_txn_hash = haltable.transact({'from': chain.web3.eth.accounts[1]}).uhalt()
    chain.wait.for_receipt(set_txn_hash)
    pass
  except Exception as e:
    pass

  halted = haltable.call().halted()
  assert halted == True 