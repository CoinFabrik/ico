import time
from datetime import datetime, timezone
from eth_utils import to_checksum_address

def config_f(network):

  config = {}

  ether = 10 ** 18

  eur_per_fulltokens = [0.05, 0.06, 0.07, 0.08, 0.10]

  def to_tokens(price):
    return int(ether / price);

  tokens_per_eur = list(map(to_tokens, eur_per_fulltokens))

  tranches_quantity = len(tokens_per_eur)

  amounts = [210000000, 420000000, 630000000, 840000000, 1008000000]

  ico_tranches_quantity = len(amounts)

  def toWei(x):
    return x*ether

  amounts = list(map(toWei, amounts))

  assert len(amounts) == len(eur_per_fulltokens),  "Fails lengths"

  config['tranches'] = []

  #Main net configuration
  config['startTime'] = int(datetime(2018, 4, 16, 10, tzinfo = timezone.utc).timestamp())
  config['endTime'] = int(datetime(2018, 7, 14, 10, tzinfo = timezone.utc).timestamp())
  config['MW_address'] = "0x93C4a8ed12BAb494bc3045380EE1CfC07507D234"
  config['token_retriever_account'] = '0x54d9249C776C56520A62faeCB87A00E105E8c9Dc'

  config['multisig_supply'] = 252 * (10 ** 5) * ether
  config['crowdsale_supply'] = 1008 * (10 ** 6) * ether
  config['token_decimals'] = 18
  config['max_tokens_to_sell'] = 1008 * (10 ** 6) * ether

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