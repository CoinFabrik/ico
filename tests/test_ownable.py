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

@pytest.fixture(scope="module")
def contract():
  return Contract()

@pytest.fixture(scope="module")
def deploy(contract, owners, web3):
  tx_hash = contract.deploy("./build/", "Ownable", tx_args(owners[0], gas=4000000),)
  return tx_hash

@pytest.fixture
def get_owner(contract):
  return contract.contract.functions.owner().call()

def test_deploy(deploy, web3):
  assert web3.eth.waitForTransactionReceipt(deploy).status

def test_first_owner(get_owner, owners):
  assert get_owner == owners[0]

def test_ownership_transfer(web3, contract, owners):
  tx_hash = contract.contract.functions.transferOwnership(owners[1]).transact(tx_args(owners[0], gas=4000000))
  assert web3.eth.waitForTransactionReceipt(tx_hash).status

def test_second_owner(get_owner, owners):
  assert get_owner == owners[1]