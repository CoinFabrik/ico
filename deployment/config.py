import time
from datetime import datetime
from eth_utils import to_checksum_address

def config_f(network):

	config = {}

	tokens_per_wei = [410, 390, 370, 350, 340, 330, 320, 310, 300, 290, 280]
	
	tranches_quantity = len(tokens_per_wei)

	amounts = [3500000, 7000000, 10500000]

	pre_ico_tranches_quantity = len(amounts)

	ico_tranches_quantity = tranches_quantity - pre_ico_tranches_quantity

	auxNum = 525*(10**4)

	for x in range(pre_ico_tranches_quantity,(tranches_quantity-1)):
		amounts.append(amounts[x - 1] + auxNum)

	def toWei(x):
		return x*(10**18)

	amounts = list(map(toWei, amounts))

	config['tranches'] = []

	#Values for testing purposes only
	if (network != "liveNet"):
		
		config['multisig_owners'] = [to_checksum_address("0xf19258256b06324c7516b00bf5c76af001ee1e95")]

		config['startTime'] = int(round(time.time())) + 60 * 10

		tranches_start = config['startTime']

		pre_ico_tranches_end = config['startTime'] + 60 * 60 * 24

		ico_tranches_end = tranches_start + 60 * 60 * 24 * 2

		for x in range(0,pre_ico_tranches_quantity - 1):
			config['tranches'].append(amounts[x])
			config['tranches'].append(tranches_start)
			config['tranches'].append(pre_ico_tranches_end)
			config['tranches'].append(tokens_per_wei[x])

		for x in range(pre_ico_tranches_quantity,(tranches_quantity-1)):
			config['tranches'].append(amounts[x])
			config['tranches'].append(tranches_start)
			config['tranches'].append(ico_tranches_end)
			config['tranches'].append(tokens_per_wei[x])
			ico_tranches_end += 60*60*24

		config['endTime'] = config['tranches'][len(config['tranches'])-2]
	else:
		#Main net configuration
		config['startTime'] = int(datetime(2017, 11, 23).timestamp())
		config['endTime'] = int(datetime(2018, 2, 20).timestamp())
		config['MW_address'] = "0xA8c39c22822a89bC8EAC413a1FFb93b73fb9c906"

		tranches_start = int(datetime(2017, 11, 19, 18).timestamp())

		tranches_end = [int(datetime(2017, 11, 30).timestamp()),
		                int(datetime(2017, 12, 7).timestamp()),
		                int(datetime(2017, 12, 18).timestamp()),
		                int(datetime(2017, 12, 25).timestamp()),
		                int(datetime(2018, 1, 1).timestamp()),
		                int(datetime(2018, 1, 8).timestamp()),
		                int(datetime(2018, 1, 15).timestamp()),
		                int(datetime(2018, 1, 22).timestamp()),
		                int(datetime(2018, 2, 2).timestamp()),
		                int(datetime(2018, 2, 14).timestamp()),
		                config['endTime']]

		for x in range(0,(tranches_quantity-1)):
			config['tranches'].append(amounts[x])
			config['tranches'].append(tranches_start)
			config['tranches'].append(tranches_end[x])
			config['tranches'].append(tokens_per_wei[x])

	return config