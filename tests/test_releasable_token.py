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
def releaseAgent(web3):
  return web3.eth.accounts[1]

@pytest.fixture(scope="module")
def transferAgent(web3):
  return web3.eth.accounts[2]

@pytest.fixture(scope="module")
def not_owner(web3):
  return web3.eth.accounts[3]

@pytest.fixture(scope="module")
def not_releaseAgent(web3):
  return web3.eth.accounts[4]

@pytest.fixture(scope="module")
def not_transferAgent(web3):
  return web3.eth.accounts[5]

@pytest.fixture(scope="module")
def recipient(web3):
  return web3.eth.accounts[6]

@pytest.fixture(scope="module")
def approved_sender(web3):
  return web3.eth.accounts[7]

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
def releasable_token():
  return Contract()

@pytest.fixture
def deploy(wait, owner):
  def inner_deploy(contract, contract_name, gas):
    tx_hash = contract.deploy("./build/", contract_name, tx_args(owner, gas=gas),)
    wait(tx_hash)
    return tx_hash
  return inner_deploy

@pytest.fixture
def releasedTrue(wait, status, owner, releaseAgent):
  def inner_releasedTrue(releasable_token, agent):
    tx_hash = releasable_token.contract.functions.setReleaseAgent(releaseAgent).transact(tx_args(owner, gas=300000))
    wait(tx_hash)
    tx_hash = releasable_token.contract.functions.releaseTokenTransfer().transact(tx_args(agent, gas=300000))
    return status(tx_hash)
  return inner_releasedTrue

@pytest.fixture
def deployment_status(releasable_token, deploy, status):
  def inner_deployment_status(gas):
    return status(deploy(releasable_token, "ReleasableTokenMock", gas))
  return inner_deployment_status

@pytest.fixture
def setReleaseAgent(releasable_token, releaseAgent, status, deploy, releasedTrue):
  def inner_setReleaseAgent(current_owner, released):
    deploy(releasable_token, "ReleasableTokenMock", 3000000)
    if released:
      releasedTrue(releasable_token, releaseAgent)
      tx_hash = releasable_token.contract.functions.setReleaseAgent(releaseAgent).transact(tx_args(current_owner, gas=300000))
      return status(tx_hash)
    else:
      tx_hash = releasable_token.contract.functions.setReleaseAgent(releaseAgent).transact(tx_args(current_owner, gas=300000))
      return status(tx_hash)
  return inner_setReleaseAgent

@pytest.fixture
def setTransferAgent(releasable_token, transferAgent, status, deploy, releasedTrue, releaseAgent):
  def inner_setTransferAgent(current_owner, released):
    deploy(releasable_token, "ReleasableTokenMock", 3000000)
    if released:
      releasedTrue(releasable_token, releaseAgent)
      tx_hash = releasable_token.contract.functions.setTransferAgent(transferAgent, True).transact(tx_args(current_owner, gas=300000))
      return status(tx_hash)
    else:
      tx_hash = releasable_token.contract.functions.setTransferAgent(transferAgent, True).transact(tx_args(current_owner, gas=300000))
      return status(tx_hash)
  return inner_setTransferAgent

@pytest.fixture
def releaseTokenTransfer(releasable_token, deploy, releasedTrue):
  def inner_releaseTokenTransfer(agent):
    deploy(releasable_token, "ReleasableTokenMock", 3000000)
    return releasedTrue(releasable_token, agent)
  return inner_releaseTokenTransfer

@pytest.fixture
def transfer(releasable_token, owner, recipient, wait, status, transferAgent, deploy, releasedTrue, releaseAgent):
  def inner_transfer(released, current_transferAgent):
    deploy(releasable_token, "ReleasableTokenMock", 3000000)
    tx_hash = releasable_token.contract.functions.setTransferAgent(transferAgent, True).transact(tx_args(owner, gas=300000))
    wait(tx_hash)
    tx_hash = releasable_token.contract.functions.mint(current_transferAgent, 1000000).transact(tx_args(owner, gas=300000))
    wait(tx_hash)
    if released:
      releasedTrue(releasable_token, releaseAgent)
      tx_hash = releasable_token.contract.functions.transfer(recipient, 10000).transact(tx_args(current_transferAgent, gas=300000))
      return status(tx_hash)
    else:
      tx_hash = releasable_token.contract.functions.transfer(recipient, 10000).transact(tx_args(current_transferAgent, gas=300000))
      return status(tx_hash)
  return inner_transfer

@pytest.fixture
def transferFrom(releasable_token, owner, recipient, wait, status, transferAgent, deploy, releasedTrue, releaseAgent, approved_sender):
  def inner_transferFrom(released, sender):
    deploy(releasable_token, "ReleasableTokenMock", 3000000)
    tx_hash = releasable_token.contract.functions.setTransferAgent(transferAgent, True).transact(tx_args(owner, gas=300000))
    wait(tx_hash)
    tx_hash = releasable_token.contract.functions.mint(sender, 1000000).transact(tx_args(owner, gas=300000))
    wait(tx_hash)
    tx_hash = releasable_token.contract.functions.approve(approved_sender, 20000).transact(tx_args(sender, gas=300000))
    wait(tx_hash)
    if released:
      releasedTrue(releasable_token, releaseAgent)
      tx_hash = releasable_token.contract.functions.transferFrom(sender, recipient, 10000).transact(tx_args(approved_sender, gas=300000))
      return status(tx_hash)
    else:
      tx_hash = releasable_token.contract.functions.transferFrom(sender, recipient, 10000).transact(tx_args(approved_sender, gas=300000))
      return status(tx_hash)
  return inner_transferFrom

@pytest.fixture
def released(deploy, releasable_token):
  deploy(releasable_token, "ReleasableTokenMock", 3000000)
  released = releasable_token.contract.functions.released().call()
  releaseAgent = releasable_token.contract.functions.releaseAgent().call()
  return released, releaseAgent


def test_deployment_failed_with_low_gas(deployment_status):
  with pytest.raises(ValueError):
    deployment_status(200000)

def test_deployment_failed_with_intrinsic_gas_too_low(deployment_status):
  assert deployment_status(300000) == 0

def test_deployment_successful_with_enough_gas(deployment_status):
  assert deployment_status(3000000) == 1

def test_released(released):
  print(released)
  

@pytest.mark.parametrize("released", [False, True])
@pytest.mark.parametrize("retrieved_owner", ["owner", "not_owner"])
def test_all_cases_of_setReleaseAgent(setReleaseAgent, owner, request, retrieved_owner, released):
  current_owner = request.getfixturevalue(retrieved_owner)
  if not released and current_owner == owner:
    assert setReleaseAgent(current_owner, released) == 1
  else:
    assert setReleaseAgent(current_owner, released) == 0


@pytest.mark.parametrize("released", [False, True])
@pytest.mark.parametrize("retrieved_owner", ["owner", "not_owner"])
def test_all_cases_of_setTransferAgent(setTransferAgent, owner, request, retrieved_owner, released):
  current_owner = request.getfixturevalue(retrieved_owner)
  if not released and current_owner == owner:
    assert setTransferAgent(current_owner, released) == 1
  else:
    assert setTransferAgent(current_owner, released) == 0


@pytest.mark.parametrize("agent", ["not_releaseAgent", "releaseAgent"])
def test_all_cases_of_releaseTokenTransfer(releaseTokenTransfer, releaseAgent, request, agent):
  release_agent = request.getfixturevalue(agent)
  if release_agent == releaseAgent:
    assert releaseTokenTransfer(release_agent) == 1
  else:
    assert releaseTokenTransfer(release_agent) == 0


@pytest.mark.parametrize("released", [False, True])
@pytest.mark.parametrize("agent", ["not_transferAgent", "transferAgent"])
def test_all_cases_of_transfer(transfer, not_transferAgent, released, agent, request):
  transfer_agent = request.getfixturevalue(agent)
  if not released and transfer_agent == not_transferAgent:
    assert transfer(released, transfer_agent) == 0
  else:
    assert transfer(released, transfer_agent) == 1


@pytest.mark.parametrize("released", [False, True])
@pytest.mark.parametrize("agent", ["not_transferAgent", "transferAgent"])
def test_all_cases_of_transferFrom(transferFrom, not_transferAgent, released, agent, request):
  transfer_agent = request.getfixturevalue(agent)
  if not released and transfer_agent == not_transferAgent:
    assert transferFrom(released, transfer_agent) == 0
  else:
    assert transferFrom(released, transfer_agent) == 1
