import time
from datetime import datetime
from eth_utils import to_checksum_address

def config_f(network):

	config = {}

	ether = 10 ** 18

	eur_per_fulltokens = [0.03, 0.04, 0.05, 0.07, 0.08, 0.1, 0.12, 0.15, 0.2]

	def to_divided(price):
		return int(ether/price);

	tokens_per_eur = list(map(to_divided, ))
	
	tranches_quantity = len(tokens_per_wei)

	amounts = [200000000, 400000000, 600000000, 900000000, 1200000000, 1500000000, 1800000000, 2100000000, 2166000000]

	ico_tranches_quantity = len(amounts)

	def toWei(x):
		return x*(10**18)

	amounts = list(map(toWei, amounts))

	assert len(amounts) == len(eur_per_fulltokens),  "Fails lengths"

	config['tranches'] = []

	#Values for testing purposes only
	if (network != "liveNet"):
		
		config['multisig_owners'] = [to_checksum_address("0xf19258256b06324c7516b00bf5c76af001ee1e95")]

		config['startTime'] = int(round(time.time())) + 60 * 10

		tranches_start = config['startTime']

		ico_tranches_end = tranches_start + 60 * 60 * 24 * 2

		for x in range(0,  tranches_quantity):
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

		tranches_start = [int(datetime(2017, 11, 19, 18).timestamp())]																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																							

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

		for x in range(0, tranches_quantity):
			config['tranches'].append(amounts[x])
			config['tranches'].append(tranches_start)
			config['tranches'].append(tranches_end[x])
			config['tranches'].append(tokens_per_wei[x])

	return config