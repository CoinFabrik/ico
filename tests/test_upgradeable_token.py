#!/usr/bin/env python3

import pytest
import sys
sys.path.append("../deployment")
from contract import Contract
from tx_args import tx_args
from web3_interface import Web3Interface


ADDRESS_ZERO = "0x0000000000000000000000000000000000000000"


@pytest.fixture(scope="module")
def address_zero():
  return ADDRESS_ZERO

@pytest.fixture(scope="module")
def owner(web3):
  return web3.eth.accounts[0]

@pytest.fixture(scope="module")
def upgradeMaster(web3):
  return web3.eth.accounts[1]

@pytest.fixture(scope="module")
def not_upgradeMaster(web3):
  return web3.eth.accounts[2]

@pytest.fixture(scope="module")
def total_supply():
  return 100000

@pytest.fixture(scope="module")
def half_supply():
  return 50000

@pytest.fixture(scope="module")
def value_zero():
  return 0

@pytest.fixture(scope="module")
def upgradingState():
  return 4

@pytest.fixture(scope="module")
def readyToUpgradeState():
  return 3

@pytest.fixture(scope="module")
def waitingForUpgradeAgentState():
  return 2

@pytest.fixture(scope="module")
def notAllowedState():
  return 1

@pytest.fixture(scope="module")
def false():
  return False

@pytest.fixture(scope="module")
def true():
  return True

@pytest.fixture(scope="module")
def status(wait):
  def inner_status(tx_hash):
    return wait(tx_hash).status
  return inner_status

@pytest.fixture(scope="module")
def wait(web3):
  def inner_wait(tx_hash):
    return web3.eth.waitForTransactionReceipt(tx_hash, timeout=10)
  return inner_wait

@pytest.fixture
def upgradeable_token():
  return Contract()

@pytest.fixture
def upgrade_agent(owner, total_supply, wait):
  upgrade_agent = Contract()
  tx_hash = upgrade_agent.deploy("./build/", "UpgradeAgentMock", tx_args(owner, gas=3000000), total_supply)
  wait(tx_hash)
  return upgrade_agent.contract.address

@pytest.fixture
def deploy(wait, upgradeMaster):
  def inner_deploy(contract, contract_name, gas, supply):
    tx_hash = contract.deploy("./build/", contract_name, tx_args(upgradeMaster, gas=gas), supply)
    wait(tx_hash)
    return tx_hash
  return inner_deploy

@pytest.fixture
def deployment_status(upgradeable_token, deploy, status, total_supply):
  def inner_deployment_status(gas):
    return status(deploy(upgradeable_token, "UpgradeableTokenMock", gas, total_supply))
  return inner_deployment_status


@pytest.fixture
def changeUpgradeMaster(upgradeable_token, not_upgradeMaster, status, deploy, total_supply):
  def inner_changeUpgradeMaster(current_master):
    deploy(upgradeable_token, "UpgradeableTokenMock", 3000000, total_supply)
    tx_hash = upgradeable_token.contract.functions.changeUpgradeMaster(not_upgradeMaster).transact(tx_args(current_master, gas=300000))
    return status(tx_hash)
  return inner_changeUpgradeMaster

@pytest.fixture
def setUpgradeAgent(upgradeable_token, deploy, status, wait, address_zero, total_supply, upgradeMaster):
  def inner_setUpgradeAgent(master, canUp, agent, state, supply):
    deploy(upgradeable_token, "UpgradeableTokenMock", 3000000, supply)
    if not canUp:
      tx_hash = upgradeable_token.contract.functions.setCanUp(canUp).transact(tx_args(master, gas=300000))
      wait(tx_hash)
    if canUp and agent != address_zero and state == 4 and supply == total_supply and master == upgradeMaster:
      tx_hash = upgradeable_token.contract.functions.setUpgradeAgent(agent).transact(tx_args(master, gas=300000))
      wait(tx_hash)
      tx_hash = upgradeable_token.contract.functions.upgrade(supply).transact(tx_args(master, gas=300000))
      wait(tx_hash)
    tx_hash = upgradeable_token.contract.functions.setUpgradeAgent(agent).transact(tx_args(master, gas=300000))
    return status(tx_hash)
  return inner_setUpgradeAgent

@pytest.fixture
def upgrade(upgradeable_token, upgrade_agent, upgradeMaster, status, wait, deploy, total_supply, half_supply, notAllowedState, readyToUpgradeState, upgradingState):
  def inner_upgrade(state, value):
    deploy(upgradeable_token, "UpgradeableTokenMock", 3000000, total_supply)
    tx_hash = upgradeable_token.contract.functions.setUpgradeAgent(upgrade_agent).transact(tx_args(upgradeMaster, gas=300000))
    wait(tx_hash)
    if state == notAllowedState:
      tx_hash = upgradeable_token.contract.functions.setCanUp(False).transact(tx_args(upgradeMaster, gas=300000))
      wait(tx_hash)
      tx_hash = upgradeable_token.contract.functions.upgrade(value).transact(tx_args(upgradeMaster, gas=300000))
    if state == upgradingState:
      tx_hash = upgradeable_token.contract.functions.upgrade(half_supply).transact(tx_args(upgradeMaster, gas=300000))
      wait(tx_hash)
      tx_hash = upgradeable_token.contract.functions.upgrade(value).transact(tx_args(upgradeMaster, gas=300000))
    if state == readyToUpgradeState:
      tx_hash = upgradeable_token.contract.functions.upgrade(value).transact(tx_args(upgradeMaster, gas=300000))
    return status(tx_hash)
  return inner_upgrade

@pytest.fixture
def varss(deploy, upgradeable_token, total_supply):
  deploy(upgradeable_token, "UpgradeableTokenMock", 3000000, total_supply)
  upgradeMaster = upgradeable_token.contract.functions.upgradeMaster().call()
  totalUpgraded = upgradeable_token.contract.functions.totalUpgraded().call()
  return upgradeMaster, totalUpgraded

def test_deployment_failed_with_low_gas(deployment_status):
  with pytest.raises(ValueError):
    deployment_status(200000)

def test_deployment_failed_with_intrinsic_gas_too_low(deployment_status):
  assert deployment_status(300000) == 0

def test_deployment_successful_with_enough_gas(deployment_status):
  assert deployment_status(3000000) == 1
  
def test_getter(varss):
  print(varss)
  
def test_failed_changeUpgradeMaster_with_wrong_master(changeUpgradeMaster, not_upgradeMaster):
  assert changeUpgradeMaster(not_upgradeMaster) == 0

def test_failed_changeUpgradeMaster_with_master_zero(changeUpgradeMaster, address_zero):
  with pytest.raises(ValueError):
    changeUpgradeMaster(address_zero)

def test_successful_changeUpgradeMaster_with_right_master(changeUpgradeMaster, upgradeMaster):
  assert changeUpgradeMaster(upgradeMaster) == 1

@pytest.mark.parametrize("state", ["readyToUpgradeState", "upgradingState"])
@pytest.mark.parametrize("canUp", ["false", "true"])
@pytest.mark.parametrize("master", ["not_upgradeMaster", "upgradeMaster"])
@pytest.mark.parametrize("agent", ["address_zero", "upgrade_agent"])
@pytest.mark.parametrize("supply", ["total_supply", "half_supply"])
def test_all_cases_of_setUpgradeAgent(setUpgradeAgent, master, canUp, agent, state, supply, upgradeMaster, address_zero, upgradingState, total_supply, request):
  master = request.getfixturevalue(master)
  canUp = request.getfixturevalue(canUp)
  agent = request.getfixturevalue(agent)
  state = request.getfixturevalue(state)
  supply = request.getfixturevalue(supply)
  if master == upgradeMaster and canUp and agent != address_zero and state != upgradingState and supply == total_supply:
    assert setUpgradeAgent(master, canUp, agent, state, supply) == 1
  else:
    assert setUpgradeAgent(master, canUp, agent, state, supply) == 0

@pytest.mark.parametrize("state", ["notAllowedState", "readyToUpgradeState", "upgradingState"])
@pytest.mark.parametrize("value", ["total_supply", "half_supply", "value_zero"])
def test_all_cases_of_upgrade(request, upgrade, state, value, readyToUpgradeState, upgradingState):
  state = request.getfixturevalue(state)
  value = request.getfixturevalue(value)
  if value != 0 and (state == readyToUpgradeState or state == upgradingState):
    assert upgrade(state, value) == 1
  else:
    assert upgrade(state, value) == 0