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
def recipient(web3):
  return web3.eth.accounts[1]

@pytest.fixture(scope="module")
def from_address(web3):
  return web3.eth.accounts[2]

@pytest.fixture(scope="module")
def middleThan():
  return 600

@pytest.fixture(scope="module")
def lessThan():
  return 400

@pytest.fixture(scope="module")
def greaterThan():
  return 800

@pytest.fixture(scope="module")
def zero():
  return 0

@pytest.fixture(scope="module")
def not_zero():
  return 1000

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
def standard_token():
  return Contract()

@pytest.fixture
def deploy(wait, owner):
  def inner_deploy(contract, contract_name, gas):
    tx_hash = contract.deploy("./build/", contract_name, tx_args(owner, gas=gas),)
    wait(tx_hash)
    return tx_hash
  return inner_deploy

@pytest.fixture
def deployment_status(standard_token, deploy, status):
  def inner_deployment_status(gas):
    return status(deploy(standard_token, "StandardTokenMock", gas))
  return inner_deployment_status


@pytest.fixture
def transfer(standard_token, owner, recipient, from_address, wait, status, deploy):
  def inner_transfer(value):
    deploy(standard_token, "StandardTokenMock", 3000000)
    tx_hash = standard_token.contract.functions.mint(from_address, 600).transact(tx_args(owner, gas=300000))
    wait(tx_hash)
    tx_hash = standard_token.contract.functions.transfer(recipient, value).transact(tx_args(from_address, gas=300000))
    return status(tx_hash)
  return inner_transfer


@pytest.fixture
def transferFrom(standard_token, owner, recipient, from_address, wait, status, deploy):
  def inner_transferFrom(value):
    deploy(standard_token, "StandardTokenMock", 3000000)
    tx_hash = standard_token.contract.functions.mint(from_address, 700).transact(tx_args(owner, gas=300000))
    wait(tx_hash)
    tx_hash = standard_token.contract.functions.approve(owner, 500).transact(tx_args(from_address, gas=300000))
    wait(tx_hash)
    tx_hash = standard_token.contract.functions.transferFrom(from_address, recipient, value).transact(tx_args(owner, gas=300000))
    return status(tx_hash)
  return inner_transferFrom


@pytest.fixture
def approve(standard_token, owner, from_address, wait, status, deploy):
  def inner_approve(value, allowed):
    deploy(standard_token, "StandardTokenMock", 3000000)
    if allowed != 0:
      tx_hash = standard_token.contract.functions.approve(from_address, 1000).transact(tx_args(owner, gas=300000))
      wait(tx_hash)
    tx_hash = standard_token.contract.functions.approve(from_address, value).transact(tx_args(owner, gas=300000))
    return status(tx_hash)
  return inner_approve


@pytest.fixture
def addApproval(standard_token, owner, from_address, status, deploy):
  def inner_addApproval():
    deploy(standard_token, "StandardTokenMock", 3000000)
    tx_hash = standard_token.contract.functions.addApproval(from_address, 1000).transact(tx_args(owner, gas=300000))
    return status(tx_hash)
  return inner_addApproval


@pytest.fixture
def subApproval(standard_token, owner, from_address, status, deploy):
  def inner_subApproval():
    deploy(standard_token, "StandardTokenMock", 3000000)
    tx_hash = standard_token.contract.functions.subApproval(from_address, 1000).transact(tx_args(owner, gas=300000))
    return status(tx_hash)
  return inner_subApproval


@pytest.fixture
def burnTokensMock(standard_token, owner, from_address, wait, status, deploy):
  def inner_burnTokensMock(value):
    deploy(standard_token, "StandardTokenMock", 3000000)
    tx_hash = standard_token.contract.functions.mint(from_address, 500).transact(tx_args(owner, gas=300000))
    wait(tx_hash)
    tx_hash = standard_token.contract.functions.burnTokensMock(from_address, value).transact(tx_args(owner, gas=300000))
    return status(tx_hash)
  return inner_burnTokensMock


@pytest.fixture
def mint(standard_token, owner, from_address, status, deploy):
  def inner_mint():
    deploy(standard_token, "StandardTokenMock", 3000000)
    tx_hash = standard_token.contract.functions.mint(from_address, 1000).transact(tx_args(owner, gas=300000))
    return status(tx_hash)
  return inner_mint

@pytest.fixture
def balance(deploy, standard_token, address_zero, owner):
  deploy(standard_token, "StandardTokenMock", 3000000)
  abalance = standard_token.contract.functions.balanceOf(address_zero).call()
  bbalance = standard_token.contract.functions.balanceOf(owner).call()
  totalSupply = standard_token.contract.functions.totalSupply().call()
  return abalance, bbalance, totalSupply


def test_deployment_failed_with_low_gas(deployment_status):
  with pytest.raises(ValueError):
    deployment_status(100000)

def test_deployment_failed_with_intrinsic_gas_too_low(deployment_status):
  assert deployment_status(300000) == 0

def test_deployment_successful_with_enough_gas(deployment_status):
  assert deployment_status(3000000) == 1

def test_balances(balance):
  print(balance)

@pytest.mark.parametrize("value", ["lessThan", "greaterThan"])
def test_all_cases_of_transfer(transfer, request, value):
  value = request.getfixturevalue(value)
  if 500 < value:
    assert transfer(value) == 0
  else:
    assert transfer(value) == 1


@pytest.mark.parametrize("value", ["lessThan", "greaterThan", "middleThan"])
def test_all_cases_of_transferFrom(transferFrom, request, value):
  value = request.getfixturevalue(value)
  if 500 > value:
    assert transferFrom(value) == 1
  else:
    assert transferFrom(value) == 0


@pytest.mark.parametrize("value", ["zero", "not_zero"])
@pytest.mark.parametrize("allowed", ["zero", "not_zero"])
def test_all_cases_of_approve(approve, request, value, allowed):
  value = request.getfixturevalue(value)
  if value != 0 and allowed != 0:
    assert approve(value, allowed) == 0
  else:
    assert approve(value, allowed) == 1


def test_addApproval(addApproval):
  assert addApproval() == 1


def test_subApproval(subApproval):
  assert subApproval() == 1


@pytest.mark.parametrize("value", ["lessThan", "greaterThan"])
def test_all_cases_of_burnTokensMock(burnTokensMock, request, value):
  value = request.getfixturevalue(value)
  if 500 > value:
    assert burnTokensMock(value) == 1
  else:
    assert burnTokensMock(value) == 0


def test_mint(mint):
  assert mint() == 1