#!/usr/bin/env python3

from util.deployer import Deployer
from util.web3_interface import Web3Interface
from util.tx_checker import fails, succeeds
from util.test_config2 import config_f

web3 = Web3Interface().w3
eth = web3.eth
web3.miner.start(1)
deployer = Deployer()

gas = 200000
gas_price = 20000000000

owner = eth.accounts[0]
release_agent = eth.accounts[1]
non_owner = eth.accounts[2]
transfer_agent = eth.accounts[3]
non_transfer_agent = eth.accounts[4]

contribution_range = (1,2**256)

def random_contribution():
  return random.randint(*contribution_range)

def random_receiver():
  return eth.accounts[random.randint(0, eth.accounts.length-1)]

tx = {"from": owner, "value": 0, "gas": gas, "gasPrice": gas_price}

def tx_from(tx_sender):
  tx = {"from": tx_sender, "value": 0, "gas": gas, "gasPrice": gas_price}  


token, deployment_hash = deployer.deploy("./build/", "ReleasableTokenMock", tx,)


#EXAMPLE succeeds("Unhalt succeeds", haltable_contract.functions.unhalt().transact(tx))

succeeds("ReleasableToken construction shouldn't fail.", deployment_hash)

assert token.functions.released().call() == False, "Shouldn't start released"

fails("Shouldn't allow transfers from a non transfer agent", token.functions.transfer(random_receiver(), random_contribution().transact(tx_from(transfer_agent))))

fails("Shouldn't allow extracting funds from a non transfer agent", token.functions.transfer(non_transfer_agent, random_receiver(), random_contribution()).transact(tx_from(transfer_agent)))

fails("Should fail if non owner tries to set a transfer agent", token.functions.transfer(transfer_agent, True).transact(tx_from(transfer_agent)))

assert token.function.transferAgents(transfer_agent).call() == False, "Non owner shouldn't have been able to set a transfer agent"

fails("Should allow the owner to set a transfer agent", token.functions.setTransferAgent(transfer_agent, True).transact(tx_from(owner)))

assert token.function.transferAgents(transfer_agent).call() == True, "Owner should've been able to set a transfer agent"

succeeds("Should allow transfers from transfer agents", token.functions.transfer(random_receiver(), random_contribution()).transact(tx_from(transfer_agent)))

succeeds("Should allow extracting funds from a transfer agent", token.functions.transfertx_from(transfer_agent, random_receiver(), random_contribution()).transact(tx_from(non_transfer_agent)))

fails("Shouldn't allow a non owner to unset a transfer agent", token.functions.setTransferAgent(transfer_agent, False).transact(tx_from(non_owner)))

assert token.function.transferAgents(transfer_agent).call() == True, "Non owner shouldn't have been able to unset a transfer agent"

succeeds("Should allow the owner to unset a transfer agent", token.functions.setTransferAgent(transfer_agent, False).transact(tx_from(non_owner)))

assert token.function.transferAgents(transfer_agent).call() == False, "Owner should've been able to unset a transfer agent"

fails("Shouldn't allow an unset transfer agent to transfer", token.functions.transfer(random_receiver(), random_contribution()).transact(tx_from(transfer_agent)))

fails("Shouldn't allow extracting funds from an unset transfer agent", token.functions.transfertx_from(transfer_agent, random_receiver(), random_contribution()).transact(tx_from(non_transfer_agent)))

succeeds("Should allow the owner to reset a transfer agent", token.functions.setTransferAgent(transfer_agent, True).transact(tx_from(owner)))

assert token.function.transferAgents(transfer_agent).call() == True, "Owner should've been able to reset a transfer agent"

succeeds("Should allow transfers from the reset transfer agent", token.functions.transfer(non_transfer_agent, random_contribution()).transact(tx_from(transfer_agent)))

succeeds("Should allow extracting funds from the reset transfer agent", token.functions.transfertx_from(transfer_agent, random_receiver(), random_contribution()).transact(tx_from(non_transfer_agent)))

fails("Shouldn't allow a non owner to set a release agent", token.functions.setReleaseAgent(release_agent).transact(tx_from(non_owner)))

assert token.function.releaseAgent(release_agent).call() == False, "Non owner shouldn't have been able to set a release agent"

succeeds("Should allow the owner to set a release agent", token.functions.setReleaseAgent(release_agent).transact(tx_from(owner)))

assert token.function.releaseAgent(release_agent).call() == True, "Owner should've been able to set a release agent"

fails("Shouldn't allow a non owner to release the tranfers", token.functions.releaseTokenTransfer().transact(tx_from(non_owner)))

assert token.function.released().call() == False, "Non owner shouldn't have been able to release the transfers"

succeeds("Should allow the owner to release the transfers", token.functions.releaseTokenTransfer().transact(tx_from(owner)))

assert token.function.released().call() == True, "Owner should've been able to release the transfers"


for sender in eth.accounts:
  succeeds("Should allow anyone to transfer after release", token.functions.transfer(random_receiver(), random_contribution()).transact(tx_from(sender)))
  

for extraction_account in eth.accounts:
  for sender in eth.accounts:
    for receiver in eth.accounts:
      succeeds("Should allow anyone extracting funds from anyone and sending them to anyone", token.functions.transfer(extraction_account, receiver, random_contribution()).transact(tx_from(sender)))