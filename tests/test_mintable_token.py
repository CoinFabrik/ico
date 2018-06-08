#!/usr/bin/env python3

import pytest
import sys
sys.path.append("../deployment")
from contract import Contract
from tx_args import tx_args
from web3_interface import Web3Interface
from test_config import config_f


ADDRESS_ZERO = "0x0000000000000000000000000000000000000000"

@pytest.fixture(scope="module")
def config():
  return config_f()

@pytest.fixture(scope="module")
def accounts(web3):
  return [ADDRESS_ZERO, web3.eth.accounts[0], web3.eth.accounts[1], web3.eth.accounts[2]]

@pytest.fixture(scope="module")
def mintable_token1():
  return Contract()

@pytest.fixture(scope="module")
def mintable_token2():
  return Contract()

@pytest.fixture(scope="module")
def deploy_mintable_token(config):
  def inner_deploy_mintable_token(token, sender, value):
    tx_hash = token.deploy("./build/", "MintableTokenMock", tx_args(sender, gas=4000000), config['multisig_supply'], config['MW_address'], value)
    return tx_hash
  return inner_deploy_mintable_token

@pytest.fixture
def set_mint_agent():
  def inner_set_mint_agent(token, sender, mint_agent):
    return token.contract.functions.setMintAgent(mint_agent, True).transact(tx_args(sender, gas=4000000))
  return inner_set_mint_agent

@pytest.fixture
def mint():
  def inner_mint(token, sender, receiver):
    return token.contract.functions.mint(receiver, 1000000).transact(tx_args(sender, gas=4000000))
  return inner_mint


def test_deploy_mintable_token1(web3, deploy_mintable_token, mintable_token1, accounts):
  assert web3.eth.waitForTransactionReceipt(deploy_mintable_token(mintable_token1, accounts[1], True)).status

def test_set_mint_agent1(web3, set_mint_agent, accounts, mintable_token1):
  assert not web3.eth.waitForTransactionReceipt(set_mint_agent(mintable_token1, accounts[2], accounts[2])).status

def test_set_mint_agent2(web3, set_mint_agent, accounts, mintable_token1):
  assert web3.eth.waitForTransactionReceipt(set_mint_agent(mintable_token1, accounts[1], accounts[2])).status

def test_mint1(web3, mint, accounts, mintable_token1):
  assert not web3.eth.waitForTransactionReceipt(mint(mintable_token1, accounts[1], accounts[2])).status

def test_mint2(web3, mint, accounts, mintable_token1):
  assert web3.eth.waitForTransactionReceipt(mint(mintable_token1, accounts[2], accounts[1])).status

def test_deploy_mintable_token2(web3, deploy_mintable_token, mintable_token2, accounts):
  assert web3.eth.waitForTransactionReceipt(deploy_mintable_token(mintable_token2, accounts[1], False)).status

def test_set_mint_agent3(web3, set_mint_agent, accounts, mintable_token2):
  assert not web3.eth.waitForTransactionReceipt(set_mint_agent(mintable_token2, accounts[2], accounts[2])).status

def test_set_mint_agent4(web3, set_mint_agent, accounts, mintable_token2):
  assert not web3.eth.waitForTransactionReceipt(set_mint_agent(mintable_token2, accounts[1], accounts[2])).status

def test_mint3(web3, mint, accounts, mintable_token2):
  assert not web3.eth.waitForTransactionReceipt(mint(mintable_token2, accounts[1], accounts[2])).status