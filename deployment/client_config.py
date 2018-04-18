from datetime import datetime
from eth_utils import to_checksum_address

def config_f():
  def toWei(x):
    return x*(10**18)

  config = {}
  config['tranches'] = []
  config['max_tokens_to_sell'] = 525 * (10 ** 5) * (10 ** 18)
  config['token_decimals'] = 18
  config['crowdsale_supply'] = 525 * (10 ** 5) * (10 ** 18)
  config['multisig_supply'] = 525 * (10 ** 5) * (10 ** 18)

  #Main net configuration
  tokens_per_wei = [410, 390, 370, 350, 340, 330, 320, 310, 300, 290, 280]
  tranches_quantity = len(tokens_per_wei)
  amounts = [3500000, 7000000, 10500000]
  pre_ico_tranches_quantity = len(amounts)
  ico_tranches_quantity = tranches_quantity - pre_ico_tranches_quantity
  auxNum = 525*(10**4)

  for x in range(pre_ico_tranches_quantity, tranches_quantity):
    amounts.append(amounts[x - 1] + auxNum)

  amounts = list(map(toWei, amounts))

  config['start_time'] = int(datetime(2018, 4, 10).timestamp())
  config['end_time'] = int(datetime(2018, 7, 7).timestamp())
  config['multisig_address'] = to_checksum_address("0xA8c39c22822a89bC8EAC413a1FFb93b73fb9c906")
  config['token_retriever_account'] = to_checksum_address("0x0F048ff7dE76B83fDC14912246AC4da5FA755cFE")

  tranches_start = int(datetime(2018, 4, 6, 18).timestamp())

  tranches_end = [int(datetime(2018, 4, 17).timestamp()),
                  int(datetime(2018, 4, 24).timestamp()),
                  int(datetime(2018, 5, 5).timestamp()),
                  int(datetime(2018, 5, 12).timestamp()),
                  int(datetime(2018, 5, 19).timestamp()),
                  int(datetime(2018, 5, 26).timestamp()),
                  int(datetime(2018, 6, 2).timestamp()),
                  int(datetime(2018, 6, 9).timestamp()),
                  int(datetime(2018, 6, 20).timestamp()),
                  int(datetime(2018, 7, 2).timestamp()),
                  config['end_time']]

  for x in range(0, tranches_quantity):
    config['tranches'].append(amounts[x])
    config['tranches'].append(tranches_start)
    config['tranches'].append(tranches_end[x])
    config['tranches'].append(tokens_per_wei[x])

  return config