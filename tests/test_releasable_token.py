#!/usr/bin/env python3

import pytest
import sys
sys.path.append("../deployment")
from contract import Contract
from tx_args import tx_args
from web3_interface import Web3Interface


@pytest.fixture(scope="module")
def owners(web3):
  return [web3.eth.accounts[0], web3.eth.accounts[1]]

@pytest.fixture
def ownable():
  return Contract()

@pytest.fixture
def deployment_hash(ownable, owners):
  def inner_deployment_hash(gas):
    return ownable.deploy("./build/", "ReleasableToken", tx_args(owners[0], gas=gas),)
  return inner_deployment_hash

@pytest.fixture
def deployment_status(web3, deployment_hash):
  def inner_deployment_status(gas):
    while True:
      receipt = web3.eth.getTransactionReceipt()
      if web3.eth.getTransactionReceipt():
        pass
    return receipt.status #web3.eth.waitForTransactionReceipt(deployment_hash(gas), timeout=10)
  return inner_deployment_status

def test_deployment_failure_with_low_gas(deployment_status):
  with pytest.raises(ValueError):
    deployment_status(200000)

def test_deployment_failure_with_intrinsic_gas_too_low(deployment_status):
  assert deployment_status(300000) == 0
  
def test_deployment_success_with_enough_gas(deployment_status):
  assert deployment_status(3000000) == 1