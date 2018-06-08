#!/usr/bin/env python3

import pytest
import sys
sys.path.append("../deployment")
from contract import Contract
from tx_args import tx_args
from web3_interface import Web3Interface


TOKENS_TO_APPROVE = 100000

@pytest.fixture(scope="module")
def accounts(web3):
  return [web3.eth.accounts[0], web3.eth.accounts[1]]

@pytest.fixture(scope="module")
def standard_token():
  return Contract()

@pytest.fixture(scope="module")
def lost_and_found_token():
  return Contract()

@pytest.fixture(scope="module")
def deploy_standard_token(standard_token, accounts):
  tx_hash = standard_token.deploy("./build/", "StandardTokenMock", tx_args(accounts[0], gas=4000000),)
  return tx_hash

@pytest.fixture(scope="module")
def deploy_lost_and_found_token(lost_and_found_token, accounts):
  tx_hash = lost_and_found_token.deploy("./build/", "LostAndFoundTokenMock", tx_args(accounts[0], gas=4000000),)
  return tx_hash

@pytest.fixture
def get_master(lost_and_found_token):
  return lost_and_found_token.contract.functions.master().call()

@pytest.fixture
def GET_TOKENS_TO_APPROVE():
  return TOKENS_TO_APPROVE

def test_deploy_token(web3, deploy_standard_token):
  assert web3.eth.waitForTransactionReceipt(deploy_standard_token).status

def test_deploy_lost_and_found(web3, deploy_lost_and_found_token):
  assert web3.eth.waitForTransactionReceipt(deploy_lost_and_found_token).status

def test_get_master(get_master, accounts):
  assert get_master == accounts[0]

def test_failure_enable_lost_and_found(web3, lost_and_found_token, GET_TOKENS_TO_APPROVE, standard_token):
  tx_hash = lost_and_found_token.contract.functions.enableLostAndFound(web3.eth.accounts[1], GET_TOKENS_TO_APPROVE, standard_token.contract.address).transact(tx_args(web3.eth.accounts[1], gas=4000000))
  assert not web3.eth.waitForTransactionReceipt(tx_hash).status

def test_success_enable_lost_and_found(web3, lost_and_found_token, GET_TOKENS_TO_APPROVE, standard_token):
  tx_hash = lost_and_found_token.contract.functions.enableLostAndFound(web3.eth.accounts[1], GET_TOKENS_TO_APPROVE, standard_token.contract.address).transact(tx_args(web3.eth.accounts[0], gas=4000000))
  assert web3.eth.waitForTransactionReceipt(tx_hash).status