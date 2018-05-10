import time
from datetime import datetime, timezone
from eth_utils import to_checksum_address

def config_f():
  config = {}
  ether = 10 ** 18
  eur_per_fulltokens = [0.05, 0.06, 0.08, 0.10]
  def to_tokens(price):
    return int(ether / price);
  tokens_per_eur = list(map(to_tokens, eur_per_fulltokens))
  tranches_quantity = len(tokens_per_eur)
  amounts = [200000000, 867000000, 1242000000, 1442000000]
  ico_tranches_quantity = len(amounts)
  def toWei(x):
    return x*ether
  amounts = list(map(toWei, amounts))
  assert len(amounts) == len(eur_per_fulltokens),  "Fails lengths"
  config['tranches'] = []
  config['startTime'] = int(datetime(2018, 4, 17, 10, tzinfo = timezone.utc).timestamp())
  config['endTime'] = int(datetime(2018, 7, 14, 10, tzinfo = timezone.utc).timestamp())
  config['MW_address'] = to_checksum_address("0x520F1214AebF4507A02cf5C5AC7E236E772db95f")
  config['token_retriever_account'] = to_checksum_address('0x54d9249C776C56520A62faeCB87A00E105E8c9Dc') #Falta cambiar
  config['multisig_supply'] = 252 * (10 ** 5) * ether #Falta cambiar
  config['crowdsale_supply'] = 1442 * (10 ** 6) * ether
  config['token_decimals'] = 18
  tranches_start = [int(datetime.utcnow().timestamp()),
                    int(datetime.utcnow().timestamp()),
                    int(datetime.utcnow().timestamp()),
                    int(datetime.utcnow().timestamp()),
                    int(datetime.utcnow().timestamp())]
  tranches_end = [int(datetime(2018, 5, 1, 10, tzinfo = timezone.utc).timestamp()),
                  int(datetime(2018, 5, 16, 10, tzinfo = timezone.utc).timestamp()),
                  int(datetime(2018, 5, 31, 10, tzinfo = timezone.utc).timestamp()),
                  int(datetime(2018, 6, 15, 10, tzinfo = timezone.utc).timestamp()),
                  config['endTime']]
  for x in range(0, tranches_quantity):
    config['tranches'].append(amounts[x])
    config['tranches'].append(tranches_start[x])
    config['tranches'].append(tranches_end[x])
    config['tranches'].append(tokens_per_eur[x])
  return config
  #Falta cambiar todas las fechas