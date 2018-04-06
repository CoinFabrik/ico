import time
from datetime import datetime
from eth_utils import to_checksum_address

def config_f(network):
  def toWei(x):
    return x*(10**18)

  config = {}
  config['tranches'] = []
  config['max_tokens_to_sell'] = 525 * (10 ** 5) * (10 ** 18)
  config['token_decimals'] = 18
  config['crowdsale_supply'] = 525 * (10 ** 5) * (10 ** 18)
  config['multisig_supply'] = 525 * (10 ** 5) * (10 ** 18)

  if (network != "liveNet"):
    #Values for testing purposes only
    config['token_retriever_account'] = "0x0F048ff7dE76B83fDC14912246AC4da5FA755cFE"
    tokens_per_wei = [350, 300]
    tranches_quantity = len(tokens_per_wei)
    amounts = [3500000, 10500000]
    pre_ico_tranches_quantity = 1
    ico_tranches_quantity = tranches_quantity - pre_ico_tranches_quantity
    amounts = list(map(toWei, amounts))
    config['multisig_owners'] = "0xF19258256B06324C7516B00bf5C76Af001ee1E95"
    config['startTime'] = int(round(time.time())) + 150
    pre_ico_tranches_start = config['startTime'] - 150
    pre_ico_tranches_end = config['startTime']
    ico_tranches_start = config['startTime']
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

    config['endTime'] = ico_tranches_start + 3500 # config['tranches'][len(config['tranches'])-2]
  else:
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

    config['startTime'] = int(datetime(2018, 4, 10).timestamp())
    config['endTime'] = int(datetime(2018, 7, 7).timestamp())
    config['multisig_owners'] = to_checksum_address("0xA8c39c22822a89bC8EAC413a1FFb93b73fb9c906")
    config['token_retriever_account'] = "0x0F048ff7dE76B83fDC14912246AC4da5FA755cFE"

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
                    config['endTime']]

    for x in range(0, tranches_quantity):
      config['tranches'].append(amounts[x])
      config['tranches'].append(tranches_start)
      config['tranches'].append(tranches_end[x])
      config['tranches'].append(tokens_per_wei[x])

  return config