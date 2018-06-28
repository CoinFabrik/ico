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
def not_owner(web3):
  return web3.eth.accounts[1]

@pytest.fixture(scope="module")
def false():
  return False

@pytest.fixture(scope="module")
def true():
  return True

@pytest.fixture(scope="module")
def haltable():
  return Contract()

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
def deploy(wait, owner):
  def inner_deploy(contract, contract_name, gas):
    tx_hash = contract.deploy("./build/", contract_name, tx_args(owner, gas=gas),)
    wait(tx_hash)
    return tx_hash
  return inner_deploy

@pytest.fixture
def deployment_status(haltable, deploy, status):
  def inner_deployment_status(gas):
    return status(deploy(haltable, "Haltable", gas))
  return inner_deployment_status

@pytest.fixture
def halt(haltable, status, deploy):
  def inner_halt(current_owner):
    deploy(haltable, "Haltable", 3000000)
    tx_hash = haltable.contract.functions.halt().transact(tx_args(current_owner, gas=300000))
    return status(tx_hash)
  return inner_halt

@pytest.fixture
def unhalt(haltable, status, wait, deploy, owner):
  def inner_unhalt(current_owner, halted):
    deploy(haltable, "Haltable", 3000000)
    if halted:
      tx_hash = haltable.contract.functions.halt().transact(tx_args(owner, gas=300000))
      wait(tx_hash)
    tx_hash = haltable.contract.functions.unhalt().transact(tx_args(current_owner, gas=300000))
    return status(tx_hash)
  return inner_unhalt

def test_deployment_failed_with_low_gas(deployment_status):
  with pytest.raises(ValueError):
    deployment_status(70000)

def test_deployment_failed_with_intrinsic_gas_too_low(deployment_status):
  assert deployment_status(146000) == 0

def test_deployment_successful_with_enough_gas(deployment_status):
  assert deployment_status(250000) == 1

@pytest.mark.parametrize("current_owner", ["owner", "not_owner"])
def test_all_halt_cases(request, halt, owner, current_owner):
  current_owner = request.getfixturevalue(current_owner)
  if current_owner == owner:
    assert halt(current_owner) == 1
  else:
    assert halt(current_owner) == 0

@pytest.mark.parametrize("current_owner", ["owner", "not_owner"])
@pytest.mark.parametrize("halted", ["false", "true"])
def test_all_unhalt_cases(request, unhalt, owner, current_owner, halted):
  current_owner = request.getfixturevalue(current_owner)
  halted = request.getfixturevalue(halted)
  if current_owner == owner and halted:
    assert unhalt(current_owner, halted) == 1
  else:
    assert unhalt(current_owner, halted) == 0