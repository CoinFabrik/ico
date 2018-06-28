#!/usr/bin/env python3

import pytest
import sys
sys.path.append("../deployment")
from contract import Contract
from tx_args import tx_args
from web3_interface import Web3Interface


TOKENS_TO_APPROVE = 100000

@pytest.fixture(scope="module")
def standard_token():
  return Contract()

@pytest.fixture(scope="module")
def lost_and_found_token():
  return Contract()

@pytest.fixture
def GET_TOKENS_TO_APPROVE():
  return TOKENS_TO_APPROVE

@pytest.fixture(scope="module")
def master(web3):
  return web3.eth.accounts[0]

@pytest.fixture(scope="module")
def not_master(web3):
  return web3.eth.accounts[1]

@pytest.fixture(scope="module")
def agent(web3):
  return web3.eth.accounts[2]

@pytest.fixture(scope="module")
def standard_token():
  return Contract()

@pytest.fixture(scope="module")
def lost_and_found_token():
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
def deploy(wait, master):
  def inner_deploy(contract, contract_name, gas):
    tx_hash = contract.deploy("./build/", contract_name, tx_args(master, gas=gas),)
    wait(tx_hash)
    return tx_hash
  return inner_deploy

@pytest.fixture
def deployment_status(lost_and_found_token, deploy, status):
  def inner_deployment_status(gas):
    return status(deploy(lost_and_found_token, "LostAndFoundTokenMock", gas))
  return inner_deployment_status


@pytest.fixture
def enableLostAndFound(lost_and_found_token, standard_token, status, deploy, agent, GET_TOKENS_TO_APPROVE):
  def inner_enableLostAndFound(current_master):
    deploy(lost_and_found_token, "LostAndFoundTokenMock", 3000000)
    deploy(standard_token, "StandardToken", 3000000)
    tx_hash = lost_and_found_token.contract.functions.enableLostAndFound(agent,
                                                                         GET_TOKENS_TO_APPROVE,
                                                                         standard_token.contract.address).transact(tx_args(current_master, gas=300000))
    return status(tx_hash)
  return inner_enableLostAndFound


def test_deployment_failed_with_low_gas(deployment_status):
  with pytest.raises(ValueError):
    deployment_status(70000)

def test_deployment_failed_with_intrinsic_gas_too_low(deployment_status):
  assert deployment_status(146000) == 0

def test_deployment_successful_with_enough_gas(deployment_status):
  assert deployment_status(250000) == 1


@pytest.mark.parametrize("current_master", ["master", "not_master"])
def test_all_enableLostAndFound_cases(request, enableLostAndFound, master, current_master):
  current_master = request.getfixturevalue(current_master)
  if current_master == master:
    assert enableLostAndFound(current_master) == 1
  else:
    assert enableLostAndFound(current_master) == 0