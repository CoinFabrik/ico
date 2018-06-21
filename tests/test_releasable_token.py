#!/usr/bin/env python3

import pytest
import sys
sys.path.append("../deployment")
from contract import Contract
from tx_args import tx_args
from web3_interface import Web3Interface


@pytest.fixture(scope="module")
def owner(web3):
  return web3.eth.accounts[0]

@pytest.fixture(scope="module")
def releaseAgent(web3):
  return web3.eth.accounts[1]

@pytest.fixture(scope="module")
def transferAgent(web3):
  return web3.eth.accounts[2]

@pytest.fixture(scope="module")
def not_owner(web3):
  return web3.eth.accounts[3]

@pytest.fixture(scope="module")
def not_releaseAgent(web3):
  return web3.eth.accounts[4]

@pytest.fixture(scope="module")
def not_transferAgent(web3):
  return web3.eth.accounts[5]

@pytest.fixture(scope="module")
def recipient(web3):
  return web3.eth.accounts[6]

@pytest.fixture(scope="module")
def approved_sender(web3):
  return web3.eth.accounts[7]

@pytest.fixture(scope="module")
def status(web3):
  def inner_status(tx_hash):
    return web3.eth.waitForTransactionReceipt(tx_hash, timeout=10).status
  return inner_status

@pytest.fixture(scope="module")
def wait(web3):
  def inner_wait(tx_hash):
    web3.eth.waitForTransactionReceipt(tx_hash, timeout=10)
  return inner_wait

@pytest.fixture
def ownable():
  return Contract()

@pytest.fixture
def deploy(wait, owner):
  def inner_deploy(contract, contract_name, gas):
    tx_hash = contract.deploy("./build/", contract_name, tx_args(owner, gas=gas),)
    wait(tx_hash)
    return tx_hash
  return inner_deploy

@pytest.fixture
def releasedTrue(wait, status, owner, releaseAgent):
  def inner_releasedTrue(ownable, agent):
    tx_hash = ownable.contract.functions.setReleaseAgent(releaseAgent).transact(tx_args(owner, gas=300000))
    wait(tx_hash)
    tx_hash = ownable.contract.functions.releaseTokenTransfer().transact(tx_args(agent, gas=300000))
    return status(tx_hash)
  return inner_releasedTrue

@pytest.fixture
def deployment_hash(ownable, deploy):
  def inner_deployment_hash(gas):
    return deploy(ownable, "ReleasableToken", gas)
  return inner_deployment_hash

@pytest.fixture
def deployment_status(deployment_hash, status):
  def inner_deployment_status(gas):
    return status(deployment_hash(gas))
  return inner_deployment_status

@pytest.fixture
def setReleaseAgent(ownable, releaseAgent, status, deploy, releasedTrue):
  def inner_setReleaseAgent(current_owner, released):
    deploy(ownable, "ReleasableToken", 3000000)
    if released:
      releasedTrue(ownable, releaseAgent)
      tx_hash = ownable.contract.functions.setReleaseAgent(releaseAgent).transact(tx_args(current_owner, gas=300000))
      return status(tx_hash)
    else:
      tx_hash = ownable.contract.functions.setReleaseAgent(releaseAgent).transact(tx_args(current_owner, gas=300000))
      return status(tx_hash)
  return inner_setReleaseAgent

@pytest.fixture
def setTransferAgent(ownable, transferAgent, status, deploy, releasedTrue, releaseAgent):
  def inner_setTransferAgent(current_owner, released):
    deploy(ownable, "ReleasableToken", 3000000)
    if released:
      releasedTrue(ownable, releaseAgent)
      tx_hash = ownable.contract.functions.setTransferAgent(transferAgent, True).transact(tx_args(current_owner, gas=300000))
      return status(tx_hash)
    else:
      tx_hash = ownable.contract.functions.setTransferAgent(transferAgent, True).transact(tx_args(current_owner, gas=300000))
      return status(tx_hash)
  return inner_setTransferAgent

@pytest.fixture
def releaseTokenTransfer(ownable, deploy, releasedTrue):
  def inner_releaseTokenTransfer(agent):
    deploy(ownable, "ReleasableToken", 3000000)
    return releasedTrue(ownable, agent)
  return inner_releaseTokenTransfer

@pytest.fixture
def transfer(ownable, owner, recipient, wait, status, transferAgent, deploy, releasedTrue, releaseAgent):
  def inner_transfer(released, current_transferAgent):
    deploy(ownable, "ReleasableTokenMock", 3000000)
    tx_hash = ownable.contract.functions.setTransferAgent(transferAgent, True).transact(tx_args(owner, gas=300000))
    wait(tx_hash)
    tx_hash = ownable.contract.functions.mint(current_transferAgent, 1000000).transact(tx_args(owner, gas=300000))
    wait(tx_hash)
    if released:
      releasedTrue(ownable, releaseAgent)
      tx_hash = ownable.contract.functions.transfer(recipient, 10000).transact(tx_args(current_transferAgent, gas=300000))
      return status(tx_hash)
    else:
      tx_hash = ownable.contract.functions.transfer(recipient, 10000).transact(tx_args(current_transferAgent, gas=300000))
      return status(tx_hash)
  return inner_transfer

@pytest.fixture
def transferFrom(ownable, owner, recipient, wait, status, transferAgent, deploy, releasedTrue, releaseAgent, approved_sender):
  def inner_transfer(released, sender):
    deploy(ownable, "ReleasableTokenMock", 3000000)
    tx_hash = ownable.contract.functions.setTransferAgent(transferAgent, True).transact(tx_args(owner, gas=300000))
    wait(tx_hash)
    tx_hash = ownable.contract.functions.mint(sender, 1000000).transact(tx_args(owner, gas=300000))
    wait(tx_hash)
    tx_hash = ownable.contract.functions.approve(approved_sender, 20000).transact(tx_args(sender, gas=300000))
    wait(tx_hash)
    if released:
      releasedTrue(ownable, releaseAgent)
      tx_hash = ownable.contract.functions.transferFrom(sender, recipient, 10000).transact(tx_args(approved_sender, gas=300000))
      return status(tx_hash)
    else:
      tx_hash = ownable.contract.functions.transferFrom(sender, recipient, 10000).transact(tx_args(approved_sender, gas=300000))
      return status(tx_hash)
  return inner_transfer


def test_deployment_failed_with_low_gas(deployment_status):
  with pytest.raises(ValueError):
    deployment_status(200000)

def test_deployment_failed_with_intrinsic_gas_too_low(deployment_status):
  assert deployment_status(300000) == 0

def test_deployment_successful_with_enough_gas(deployment_status):
  assert deployment_status(3000000) == 1

def test_failed_setReleaseAgent_with_wrong_owner_and_released_false(setReleaseAgent, not_owner):
  assert setReleaseAgent(not_owner, False) == 0

def test_failed_setReleaseAgent_with_right_owner_and_released_true(setReleaseAgent, owner):
  assert setReleaseAgent(owner, True) == 0

def test_failed_setReleaseAgent_with_wrong_owner_and_released_true(setReleaseAgent, not_owner):
  assert setReleaseAgent(not_owner, True) == 0

def test_successful_setReleaseAgent_with_right_owner_and_released_false(setReleaseAgent, owner):
  assert setReleaseAgent(owner, False) == 1

def test_failed_setTransferAgent_with_wrong_owner_and_released_false(setTransferAgent, not_owner):
  assert setTransferAgent(not_owner, False) == 0

def test_failed_setTransferAgent_with_right_owner_and_released_true(setTransferAgent, owner):
  assert setTransferAgent(owner, True) == 0

def test_failed_setTransferAgent_with_wrong_owner_and_released_true(setTransferAgent, not_owner):
  assert setTransferAgent(not_owner, True) == 0

def test_successful_setTransferAgent_with_right_owner_and_released_false(setTransferAgent, owner):
  assert setTransferAgent(owner, False) == 1

def test_failed_releaseTokenTransfer_with_wrong_releaseAgent(releaseTokenTransfer, not_releaseAgent):
  assert releaseTokenTransfer(not_releaseAgent) == 0

def test_successful_releaseTokenTransfer_with_right_releaseAgent(releaseTokenTransfer, releaseAgent):
  assert releaseTokenTransfer(releaseAgent) == 1

def test_failed_transfer_with_release_false_and_wrong_transferAgent(transfer, not_transferAgent):
  assert transfer(False, not_transferAgent) == 0

def test_successful_transfer_with_release_true_and_wrong_transferAgent(transfer, not_transferAgent):
  assert transfer(True, not_transferAgent) == 1

def test_successful_transfer_with_release_false_and_right_transferAgent(transfer, transferAgent):
  assert transfer(False, transferAgent) == 1

def test_successful_transfer_with_release_true_and_right_transferAgent(transfer, transferAgent):
  assert transfer(True, transferAgent) == 1


def test_failed_transferFrom_with_release_false_and_wrong_transferAgent(transfer, not_transferAgent):
  assert transfer(False, not_transferAgent) == 0

def test_successful_transferFrom_with_release_true_and_wrong_transferAgent(transfer, not_transferAgent):
  assert transfer(True, not_transferAgent) == 1

def test_successful_transferFrom_with_release_false_and_right_transferAgent(transfer, transferAgent):
  assert transfer(False, transferAgent) == 1

def test_successful_transferFrom_with_release_true_and_right_transferAgent(transfer, transferAgent):
  assert transfer(True, transferAgent) == 1