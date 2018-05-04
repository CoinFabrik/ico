import time
from eth_utils import to_checksum_address

def config_f():
  def toWei(x):
    return x*(10**18)

  #Values for testing purposes only
  config = {}
  config['tranches'] = []
  config['max_tokens_to_sell'] = 525 * (10 ** 5) * (10 ** 18)
  config['token_decimals'] = 18
  config['crowdsale_supply'] = 525 * (10 ** 5) * (10 ** 18)
  config['multisig_supply'] = 525 * (10 ** 5) * (10 ** 18)
  config['token_retriever_account'] = to_checksum_address("0x0F048ff7dE76B83fDC14912246AC4da5FA755cFE")
  tokens_per_wei = [350, 300]
  tranches_quantity = len(tokens_per_wei)
  amounts = [3500000, 10500000]
  pre_ico_tranches_quantity = 1
  ico_tranches_quantity = tranches_quantity - pre_ico_tranches_quantity
  amounts = list(map(toWei, amounts))
  config['MW_address'] = to_checksum_address("0xF19258256B06324C7516B00bf5C76Af001ee1E95")
  config['start_time'] = int(round(time.time())) + 10
  pre_ico_tranches_start = config['start_time'] - 10
  pre_ico_tranches_end = config['start_time']
  ico_tranches_start = config['start_time']
  ico_tranches_end = ico_tranches_start + 60 * 60 * 24 * 2

  for x in range(pre_ico_tranches_quantity):
    config['tranches'].append(amounts[x])
    config['tranches'].append(pre_ico_tranches_start)
    config['tranches'].append(pre_ico_tranches_end)
    config['tranches'].append(tokens_per_wei[x])

  for x in range(pre_ico_tranches_quantity, tranches_quantity):
    config['tranches'].append(amounts[x])
    config['tranches'].append(ico_tranches_start)
    config['tranches'].append(ico_tranches_end)
    config['tranches'].append(tokens_per_wei[x])
    ico_tranches_end += 60*60*24

  config['end_time'] = ico_tranches_start + 105 # config['tranches'][len(config['tranches'])-2]

  return config