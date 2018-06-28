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
def not_owner(web3):
  return web3.eth.accounts[1]

@pytest.fixture(scope="module")
def ownable():
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
def deployment_status(ownable, deploy, status):
  def inner_deployment_status(gas):
    return status(deploy(ownable, "Ownable", gas))
  return inner_deployment_status

@pytest.fixture
def transferOwnership(ownable, status, deploy):
  def inner_transferOwnership(current_owner, new_owner):
    deploy(ownable, "Ownable", 3000000)
    tx_hash = ownable.contract.functions.transferOwnership(new_owner).transact(tx_args(current_owner, gas=300000))
    return status(tx_hash)
  return inner_transferOwnership


def test_deployment_failed_with_low_gas(deployment_status):
  with pytest.raises(ValueError):
    deployment_status(70000)

def test_deployment_failed_with_intrinsic_gas_too_low(deployment_status):
  assert deployment_status(146000) == 0

def test_deployment_successful_with_enough_gas(deployment_status):
  assert deployment_status(147500) == 1


@pytest.mark.parametrize("current_owner", ["owner", "not_owner"])
@pytest.mark.parametrize("new_owner", ["not_owner", "address_zero"])
def test_all_transferOwnership_cases(request, transferOwnership, owner, address_zero, current_owner, new_owner):
  current_owner = request.getfixturevalue(current_owner)
  new_owner = request.getfixturevalue(new_owner)
  if current_owner == owner and new_owner != address_zero:
    assert transferOwnership(current_owner, new_owner) == 1
  else:
    assert transferOwnership(current_owner, new_owner) == 0