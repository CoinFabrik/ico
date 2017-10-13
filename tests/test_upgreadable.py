initial_value = 1500
transfered = 57
import populus.utils.wait

def deploy_contract(chain, contract, arguments):
  Contract = chain.provider.get_contract_factory(contract)
  txn_hash = Contract.deploy(args=arguments)
  contract_address = chain.wait.for_contract_address(txn_hash)
  return Contract(address=contract_address)

def test_upgradable(chain, web3, accounts):

  upgradable = deploy_contract(chain, 'toBeUpgraded', [initial_value])

  assert upgradable

def test_not_fail_master_change(chain, web3, accounts):
  
  upgradable = deploy_contract(chain, 'toBeUpgraded', [initial_value])
  upgradable.transact().changeUpgradeMaster(accounts[1])
  master = upgradable.call().upgradeMaster()

  assert master.upper() == accounts[1].upper()

def test_fail_master_change(chain, web3, accounts):
  upgradable = deploy_contract(chain, 'toBeUpgraded', [initial_value])
  try:
    upgradable.transact({'from':accounts[1]}).changeUpgradeMaster(accounts[1])
    pass
  except Exception as e:
    pass
  
  master = upgradable.call().upgradeMaster()

  assert master.upper() == accounts[0].upper()

def test_assign_valid_agent(chain, web3, accounts):
  From = deploy_contract(chain, 'toBeUpgraded', [initial_value])
  To = deploy_contract(chain, 'toUpgrade', [initial_value])

  From.transact().setUpgradeAgent(To.address)
  agent = From.call().upgradeAgent()

  assert agent.upper() == To.address.upper()

def test_assign_invalid_agent(chain, web3, accounts):
  From = deploy_contract(chain, 'toBeUpgraded', [initial_value])
  To = deploy_contract(chain, 'toUpgrade', [initial_value+3])

  try:
    From.transact().setUpgradeAgent(To.address)
    assert False
    pass
  except Exception as e:
    pass

  agent = From.call().upgradeAgent()

  assert agent.upper() != To.address.upper()

  try:
    From.transact().setUpgradeAgent('0x0')
    assert False
    pass
  except Exception as e:
    pass

  agent = From.call().upgradeAgent()

  assert agent == '0x0000000000000000000000000000000000000000'

  try:
    From.transact().setUpgradeAgent(accounts[1])
    assert False
    pass
  except Exception as e:
    pass

  agent = From.call().upgradeAgent()

  assert agent.upper() != accounts[1].upper()

def test_assign_on_cannot_upgrade(chain, web3, accounts):
  From = deploy_contract(chain, 'toBeUpgraded', [initial_value])
  To = deploy_contract(chain, 'toUpgrade', [initial_value])

  From.transact().setCanUp(False);

  try:
    From.transact().setUpgradeAgent(To.address)
    assert False
    pass
  except Exception as e:
    pass

  agent = From.call().upgradeAgent()

  assert agent.upper() != To.address.upper()

def test_assign_on_upgrading(chain, web3, accounts):
  From = deploy_contract(chain, 'toBeUpgraded', [initial_value])
  To = deploy_contract(chain, 'toUpgrade', [initial_value])
  To2 = deploy_contract(chain, 'toUpgrade', [initial_value])

  From.transact().setUpgradeAgent(To.address)
  From.transact().upgrade(1);

  try:
    From.transact().setUpgradeAgent(To2.address)
    assert False
    pass
  except Exception as e:
    pass

  agent = From.call().upgradeAgent()

  assert agent.upper() != To2.address.upper()

def test_assign_from_non_master(chain, web3, accounts):
  From = deploy_contract(chain, 'toBeUpgraded', [initial_value])
  To = deploy_contract(chain, 'toUpgrade', [initial_value])

  try:
    From.transact({'from':accounts[1]}).setUpgradeAgent(To.address)
    assert False
    pass
  except Exception as e:
    pass

  agent = From.call().upgradeAgent()

  assert agent.upper() != To.address.upper()

def test_states(chain, web3, accounts):
  From = deploy_contract(chain, 'toBeUpgraded', [initial_value])
  To = deploy_contract(chain, 'toUpgrade', [initial_value])

  From.transact().setCanUp(False);
  state = From.call().getUpgradeState()
  assert state == 1

  From.transact().setCanUp(True);
  state = From.call().getUpgradeState()
  assert state == 2

  From.transact().setUpgradeAgent(To.address)
  state = From.call().getUpgradeState()
  assert state == 3

  From.transact().upgrade(1)
  state = From.call().getUpgradeState()
  assert state == 4

def test_upgrade(chain, web3, accounts):
  From = deploy_contract(chain, 'toBeUpgraded', [initial_value])
  To = deploy_contract(chain, 'toUpgrade', [initial_value])

  From.transact().setUpgradeAgent(To.address)
  total = From.call().totalUpgraded()
  owned = From.call().balanceOf(accounts[0])
  assert 0 == total
  assert initial_value == owned

  From.transact().upgrade(transfered)
  total = From.call().totalUpgraded()
  owned = From.call().balanceOf(accounts[0])
  assert transfered == total
  assert initial_value-transfered == owned

def test_upgrade_fail(chain, web3, accounts):
  From = deploy_contract(chain, 'toBeUpgraded', [initial_value])
  To = deploy_contract(chain, 'toUpgrade', [initial_value])

  try:
    From.transact().upgrade(transfered)
    assert False
    pass
  except Exception as e:
    pass

  total = From.call().totalUpgraded()
  owned = From.call().balanceOf(accounts[0])
  assert 0 == total
  assert initial_value == owned

  From.transact().setUpgradeAgent(To.address)
  From.transact().setCanUp(False);
  
  try:
    From.transact().upgrade(transfered)
    assert False
    pass
  except Exception as e:
    pass

  total = From.call().totalUpgraded()
  owned = From.call().balanceOf(accounts[0])
  assert 0 == total
  assert initial_value == owned