#!/usr/bin/env python3

import pytest
import sys
sys.path.append("../deployment")
from contract import Contract
from tx_args import tx_args
from web3_interface import Web3Interface


ADDRESS_ZERO = "0x0000000000000000000000000000000000000000"

@pytest.fixture(scope="module")
def masters(web3):
  return [ADDRESS_ZERO, web3.eth.accounts[0], web3.eth.accounts[1], web3.eth.accounts[2]]

@pytest.fixture(scope="module")
def upgrade_agent_contract():
  return Contract()

@pytest.fixture(scope="module")
def upgradeable_token_contract():
  return Contract()

@pytest.fixture(scope="module")
def deploy_upgrade_agent_contract(upgrade_agent_contract, masters):
  tx_hash = upgrade_agent_contract.deploy("./build/", "UpgradeAgentMock", tx_args(masters[1], gas=4000000), 1000000)
  return tx_hash

@pytest.fixture(scope="module")
def deploy_upgradeable_token_contract(upgradeable_token_contract, masters):
  tx_hash = upgradeable_token_contract.deploy("./build/", "UpgradeableTokenMock", tx_args(masters[1], gas=4000000), 1000000)
  return tx_hash

@pytest.fixture
def get_upgrade_master(upgradeable_token_contract):
  return upgradeable_token_contract.contract.functions.upgradeMaster().call()

@pytest.fixture
def change_upgrade_master(upgradeable_token_contract):
  def inner_change_upgrade_master(sender, new_master):
      return upgradeable_token_contract.contract.functions.changeUpgradeMaster(new_master).transact(tx_args(sender, gas=4000000))
  return inner_change_upgrade_master

@pytest.fixture
def get_canUp(upgradeable_token_contract):
  return upgradeable_token_contract.contract.functions.canUpgrade().call()

@pytest.fixture
def set_canUp(upgradeable_token_contract):
  def inner_set_canUp(value, sender):
      return upgradeable_token_contract.contract.functions.setCanUp(value).transact(tx_args(sender, gas=4000000))
  return inner_set_canUp

@pytest.fixture
def get_upgrade_state(upgradeable_token_contract):
  return upgradeable_token_contract.contract.functions.getUpgradeState().call()

@pytest.fixture
def set_upgrade_agent(upgradeable_token_contract):
  def inner_set_upgrade_agent(address, sender):
      return upgradeable_token_contract.contract.functions.setUpgradeAgent(address).transact(tx_args(sender, gas=4000000))
  return inner_set_upgrade_agent

@pytest.fixture
def get_upgrade_agent(upgradeable_token_contract):
  return upgradeable_token_contract.contract.functions.upgradeAgent().call()

@pytest.fixture
def upgrade(upgradeable_token_contract):
  def inner_upgrade(value, sender):
      return upgradeable_token_contract.contract.functions.upgrade(value).transact(tx_args(sender, gas=4000000))
  return inner_upgrade

@pytest.fixture
def get_total_upgraded(upgradeable_token_contract):
  return upgradeable_token_contract.contract.functions.totalUpgraded().call()


def test_deploy_upgrade_agent_contract(web3, deploy_upgrade_agent_contract):
  assert web3.eth.waitForTransactionReceipt(deploy_upgrade_agent_contract).status

def test_deploy_upgradeable_token_contract(web3, deploy_upgradeable_token_contract):
  assert web3.eth.waitForTransactionReceipt(deploy_upgradeable_token_contract).status

def test_master_1(get_upgrade_master, masters):
  assert get_upgrade_master == masters[1]

def test_change_upgrade_master1(web3, change_upgrade_master, masters):
  assert not web3.eth.waitForTransactionReceipt(change_upgrade_master(masters[2], masters[3])).status

def test_master_2(get_upgrade_master, masters):
  assert get_upgrade_master == masters[1]

def test_change_upgrade_master2(web3, change_upgrade_master, masters):
  assert not web3.eth.waitForTransactionReceipt(change_upgrade_master(masters[1], masters[0])).status

def test_master_3(get_upgrade_master, masters):
  assert get_upgrade_master == masters[1]

def test_change_upgrade_master3(web3, change_upgrade_master, masters):
  assert web3.eth.waitForTransactionReceipt(change_upgrade_master(masters[1], masters[2])).status

def test_master_4(get_upgrade_master, masters):
  assert get_upgrade_master == masters[2]

def test_change_upgrade_master4(web3, change_upgrade_master, masters):
  assert web3.eth.waitForTransactionReceipt(change_upgrade_master(masters[2], masters[1])).status

def test_master_5(get_upgrade_master, masters):
  assert get_upgrade_master == masters[1]

def test_canUp1(get_canUp):
  assert get_canUp

def test_set_canUp1(web3, set_canUp, masters):
  assert web3.eth.waitForTransactionReceipt(set_canUp(False, masters[1])).status

def test_canUp2(get_canUp):
  assert not get_canUp

def test_get_upgrade_state1(get_upgrade_state):
  assert get_upgrade_state

def test_set_upgrade_agent1(web3, set_upgrade_agent, masters, upgrade_agent_contract):
  assert not web3.eth.waitForTransactionReceipt(set_upgrade_agent(upgrade_agent_contract.contract.address, masters[2])).status

def test_set_upgrade_agent2(web3, set_upgrade_agent, masters, upgrade_agent_contract):
  assert not web3.eth.waitForTransactionReceipt(set_upgrade_agent(masters[0], masters[1])).status

def test_set_upgrade_agent3(web3, set_upgrade_agent, masters, upgrade_agent_contract):
  assert not web3.eth.waitForTransactionReceipt(set_upgrade_agent(upgrade_agent_contract.contract.address, masters[1])).status

def test_get_upgrade_agent4(get_upgrade_agent, masters):
  assert get_upgrade_agent == masters[0]

def test_upgrade1(web3, upgrade, masters):
  assert not web3.eth.waitForTransactionReceipt(upgrade(10000000000, masters[1])).status

def test_get_total_upgraded1(get_total_upgraded):
  assert not get_total_upgraded

def test_set_canUp2(web3, set_canUp, masters):
  assert web3.eth.waitForTransactionReceipt(set_canUp(True, masters[1])).status

def test_canUp3(get_canUp):
  assert get_canUp

def test_get_upgrade_state2(get_upgrade_state):
  assert get_upgrade_state == 2

def test_upgrade2(web3, upgrade, masters):
  assert not web3.eth.waitForTransactionReceipt(upgrade(10000000000, masters[1])).status

def test_get_total_upgraded2(get_total_upgraded):
  assert not get_total_upgraded

def test_set_upgrade_agent4(web3, set_upgrade_agent, masters, upgrade_agent_contract):
  assert web3.eth.waitForTransactionReceipt(set_upgrade_agent(upgrade_agent_contract.contract.address, masters[1])).status

def test_get_upgrade_agent5(get_upgrade_agent, upgrade_agent_contract):
  assert get_upgrade_agent == upgrade_agent_contract.contract.address

def test_get_upgrade_state3(get_upgrade_state):
  assert get_upgrade_state == 3

def test_upgrade3(web3, upgrade, masters):
  assert not web3.eth.waitForTransactionReceipt(upgrade(0, masters[1])).status

def test_upgrade4(web3, upgrade, masters):
  assert web3.eth.waitForTransactionReceipt(upgrade(10000000000, masters[1])).status

def test_get_total_upgraded3(get_total_upgraded):
  assert get_total_upgraded == 10000000000

def test_get_upgrade_state4(get_upgrade_state):
  assert get_upgrade_state == 4