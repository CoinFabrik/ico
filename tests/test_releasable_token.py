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

@pytest.fixture
def ownable():
  return Contract()

@pytest.fixture
def deployment_hash(ownable, owner):
  def inner_deployment_hash(gas):
    return ownable.deploy("./build/", "ReleasableToken", tx_args(owner, gas=gas),)
  return inner_deployment_hash

@pytest.fixture
def deployment_status(web3, deployment_hash):
  def inner_deployment_status(gas):
    return web3.eth.waitForTransactionReceipt(deployment_hash(gas), timeout=10).status
  return inner_deployment_status

@pytest.fixture
def setReleaseAgent(web3, ownable, owner, releaseAgent):
  def inner_setReleaseAgent(current_owner, released):
    ownable.deploy("./build/", "ReleasableToken", tx_args(owner, gas=3000000),)
    if released:
      tx_hash = ownable.contract.functions.setReleaseAgent(releaseAgent).transact(tx_args(owner, gas=300000))
      web3.eth.waitForTransactionReceipt(tx_hash, timeout=10)
      tx_hash = ownable.contract.functions.releaseTokenTransfer().transact(tx_args(releaseAgent, gas=300000))
      web3.eth.waitForTransactionReceipt(tx_hash, timeout=10)
      tx_hash = ownable.contract.functions.setReleaseAgent(releaseAgent).transact(tx_args(current_owner, gas=300000))
      return web3.eth.waitForTransactionReceipt(tx_hash, timeout=10).status
    else:
      tx_hash = ownable.contract.functions.setReleaseAgent(releaseAgent).transact(tx_args(current_owner, gas=300000))
      return web3.eth.waitForTransactionReceipt(tx_hash, timeout=10).status
  return inner_setReleaseAgent

@pytest.fixture
def setTransferAgent(web3, ownable, owner, transferAgent, releaseAgent):
  def inner_setTransferAgent(current_owner, released):
    ownable.deploy("./build/", "ReleasableToken", tx_args(owner, gas=3000000),)
    if released:
      tx_hash = ownable.contract.functions.setReleaseAgent(releaseAgent).transact(tx_args(owner, gas=300000))
      web3.eth.waitForTransactionReceipt(tx_hash, timeout=10)
      tx_hash = ownable.contract.functions.releaseTokenTransfer().transact(tx_args(releaseAgent, gas=300000))
      web3.eth.waitForTransactionReceipt(tx_hash, timeout=10)
      tx_hash = ownable.contract.functions.setTransferAgent(transferAgent, True).transact(tx_args(current_owner, gas=300000))
      return web3.eth.waitForTransactionReceipt(tx_hash, timeout=10).status
    else:
      tx_hash = ownable.contract.functions.setTransferAgent(transferAgent, True).transact(tx_args(current_owner, gas=300000))
      return web3.eth.waitForTransactionReceipt(tx_hash, timeout=10).status
  return inner_setTransferAgent

def test_deployment_failure_with_low_gas(deployment_status):
  with pytest.raises(ValueError):
    deployment_status(200000)

def test_deployment_failure_with_intrinsic_gas_too_low(deployment_status):
  assert deployment_status(300000) == 0
  
def test_deployment_success_with_enough_gas(deployment_status):
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