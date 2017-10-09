#Asumes python 3.5, populus 1.10.1
from pprint import pprint
from populus import Project
from populus.utils.wait import wait_for_transaction_receipt
import config
from web3 import Web3
from decimal import *

def check_succesful_tx(web3: Web3, txid: str, timeout=180) -> dict:
  """See if transaction went through (Solidity code did not throw).

  :return: Transaction receipt
  """

  # http://ethereum.stackexchange.com/q/6007/620
  receipt = wait_for_transaction_receipt(web3, txid, timeout=timeout)
  txinfo = web3.eth.getTransaction(txid)

  # EVM has only one error mode and it's consume all gas
  assert txinfo["gas"] != receipt["gasUsed"], "Out of Gas"
  return receipt

def  deploy(chain_name, start=0, end=0):

  project = Project()

  with project.get_chain(chain_name) as chain:

    web3 = chain.web3

    Crowdsale = chain.provider.get_contract_factory('Crowdsale');

    print("Web3 provider is", web3.currentProvider)

    #Setup of constructor params

 
    beneficiary = config.beneficiary(web3)
    assert beneficiary, "Make sure your node has coinbase account created"

    multisig_address = config.multisig_address

    print(multisig_address)

    init_times = config.init_times(chain_name)

    pprint(init_times)

    #For non mainnet start in 3 min, end in 25
    
      
    # ether_in_eur = Decimal(287.31);
    # pre_ico_tranches_quantity = 3;
    # tranches_quantity = 11;
    # pre_ico_tranches_start = 17;
    # pre_ico_tranches_end = 42;
    # ico_tranches_start = 100;
    # ico_tranches_end = 200;
    
    # eur_per_fulltokens = [Decimal(0.07), Decimal(0.08), Decimal(0.09), Decimal(0.10), Decimal(0.11), Decimal(0.12), Decimal(0.13), Decimal(0.14), Decimal(0.15), Decimal(0.16), Decimal(0.17)];

    # tokens_per_wei = list( map( lambda x: (ether_in_eur/x).to_integral_value(), eur_per_fulltokens ) );
    
    # amounts = [Decimal(60000), Decimal(120000), Decimal(200000)];

    # for (let i = pre_ico_tranches_quantity; i < tranches_quantity; i++) {
    #   amounts.push(Decimal(amounts[i-1] + 50000000));
    # }
    # amounts.forEach(function(amount) {
    #   return amount.times(10**18);
    # });

    tranches = [15,init_times['startTime']+1*60*60, init_times['startTime']+2*60*60+1, 15 ];

    txhash = Crowdsale.deploy(transaction={"from": beneficiary, 'gas': 6650000}, args=[multisig_address, init_times['startTime'], init_times['endTime'], beneficiary, tranches])
    print("Deploying crowdsale, tx hash is", txhash)
    receipt = check_succesful_tx(web3, txhash)
    crowdsale_address = receipt["contractAddress"]
    print("Crowdsale contract address is", crowdsale_address)


# deploy('testrpc')








