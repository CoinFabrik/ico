from decimal import *
import time

getcontext().prec = 425000000
getcontext().Emax = 999

multisig_address = "0x83917f644df1319a6ae792bb244333332e65fff8"

def beneficiary(web3):

  return web3.eth.coinbase

def init_times(chain_name):
  now = int(time.time())

  #For non mainnet start in 3 min, end in 25
  if (chain_name != 'mainnet'):
    startTime = now + 1*60*60+3*60
    endTime = now + 27*60*60
  else:
    startTime = 1515202012123232
    endTime = 132135135153153153

  return dict({'startTime': startTime, 'endTime': endTime})


  
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