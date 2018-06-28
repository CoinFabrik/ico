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
def token_tranche_pricing():
  return Contract()

@pytest.fixture
def deploy(wait, owner):
  def inner_deploy(contract, contract_name, gas):
    tx_hash = contract.deploy("./build/", contract_name, tx_args(owner, gas=gas),)
    wait(tx_hash)
    return tx_hash
  return inner_deploy

@pytest.fixture
def deployment_status(token_tranche_pricing, deploy, status):
  def inner_deployment_status(gas):
    return status(deploy(token_tranche_pricing, "TokenTranchePricingMock", gas))
  return inner_deployment_status