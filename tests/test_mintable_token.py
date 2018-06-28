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
def multisig_wallet(config):
  return config["MW_address"]

@pytest.fixture(scope="module")
def initial_supply(config):
  return config["multisig_supply"]

@pytest.fixture(scope="module")
def owner(web3):
  return web3.eth.accounts[0]

@pytest.fixture(scope="module")
def not_owner(web3):
  return web3.eth.accounts[1]

@pytest.fixture(scope="module")
def mintAgent(web3):
  return web3.eth.accounts[2]

@pytest.fixture(scope="module")
def not_mintAgent(web3):
  return web3.eth.accounts[3]

@pytest.fixture(scope="module")
def receiver(web3):
  return web3.eth.accounts[4]

@pytest.fixture(scope="module")
def false():
  return False

@pytest.fixture(scope="module")
def true():
  return True

@pytest.fixture(scope="module")
def zero():
  return 0

@pytest.fixture(scope="module")
def address_zero():
  return ADDRESS_ZERO

@pytest.fixture(scope="module")
def mintable_token():
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
  def inner_deploy(contract, contract_name, gas, *args):
    tx_hash = contract.deploy("./build/", contract_name, tx_args(owner, gas=gas), *args)
    wait(tx_hash)
    return tx_hash
  return inner_deploy

@pytest.fixture
def deployment_status(mintable_token, deploy, status):
  def inner_deployment_status(gas, *args):
    return status(deploy(mintable_token, "MintableTokenMock", gas, *args))
  return inner_deployment_status


@pytest.fixture
def mint(mintable_token, status, wait, deploy, config, mintAgent, owner, receiver):
  def inner_mint(current_mint_agent, canMint):
    if canMint:
      deploy(mintable_token, "MintableTokenMock", 450000, config["multisig_supply"], config["MW_address"], True)
      tx_hash = mintable_token.contract.functions.setMintAgent(mintAgent, True).transact(tx_args(owner, gas=300000))
      wait(tx_hash)
    else:
      deploy(mintable_token, "MintableTokenMock", 450000, config["multisig_supply"], config["MW_address"], False)
    tx_hash = mintable_token.contract.functions.mint(receiver, 100000).transact(tx_args(current_mint_agent, gas=300000))
    return status(tx_hash)
  return inner_mint

@pytest.fixture
def setMintAgent(mintable_token, status, deploy, config, mintAgent):
  def inner_setMintAgent(current_owner, canMint):
    if canMint:
      deploy(mintable_token, "MintableTokenMock", 450000, config["multisig_supply"], config["MW_address"], True)
    else:
      deploy(mintable_token, "MintableTokenMock", 450000, config["multisig_supply"], config["MW_address"], False)
    tx_hash = mintable_token.contract.functions.setMintAgent(mintAgent, True).transact(tx_args(current_owner, gas=300000))
    return status(tx_hash)
  return inner_setMintAgent


def test_deployment_failed_with_low_gas(deployment_status, config):
  with pytest.raises(ValueError):
    deployment_status(70000, config["multisig_supply"], config["MW_address"], True)

def test_deployment_failed_with_intrinsic_gas_too_low(deployment_status, config):
  assert deployment_status(300000, config["multisig_supply"], config["MW_address"], True) == 0

def test_deployment_successful_with_enough_gas(deployment_status, config):
  assert deployment_status(450000, config["multisig_supply"], config["MW_address"], True) == 1
  

@pytest.mark.parametrize("multisig", ["multisig_wallet", "address_zero"])
@pytest.mark.parametrize("mintable", ["false", "true"])
@pytest.mark.parametrize("initialSupply", ["zero", "initial_supply"])
def test_rest_of_deployment_cases(request, deployment_status, multisig, mintable, initialSupply, address_zero):
  multisig = request.getfixturevalue(multisig)
  mintable = request.getfixturevalue(mintable)
  initialSupply = request.getfixturevalue(initialSupply)
  if multisig != address_zero and (mintable or initialSupply != 0):
    assert deployment_status(450000, initialSupply, multisig, mintable) == 1
  else:
    assert deployment_status(450000, initialSupply, multisig, mintable) == 0


@pytest.mark.parametrize("mint_agent", ["mintAgent", "not_mintAgent"])
@pytest.mark.parametrize("canMint", ["false", "true"])
def test_all_mint_cases(request, mint, mint_agent, canMint, mintAgent):
  mint_agent = request.getfixturevalue(mint_agent)
  canMint = request.getfixturevalue(canMint)
  if mint_agent == mintAgent and canMint:
    assert mint(mint_agent, canMint) == 1
  else:
    assert mint(mint_agent, canMint) == 0


@pytest.mark.parametrize("current_owner", ["mintAgent", "not_mintAgent"])
@pytest.mark.parametrize("canMint", ["false", "true"])
def test_all_setMintAgent_cases(request, setMintAgent, current_owner, canMint, owner):
  current_owner = request.getfixturevalue(current_owner)
  canMint = request.getfixturevalue(canMint)
  if current_owner == owner and canMint:
    assert setMintAgent(current_owner, canMint) == 1
  else:
    assert setMintAgent(current_owner, canMint) == 0