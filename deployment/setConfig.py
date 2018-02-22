import sys

if len(sys.argv) == 1:
	from config import config_f
elif sys.argv[1] == 'test':
	from configTest import config_t as config_f
else:
	sys.exit("Unknown argument: " + sys.argv[1])

from datetime import datetime
import json
import time
import os, errno
import testing

crowdsale_contract = None
web3 = None
gas = None
gas_price = None
accounts = None
token_address = None
token_contract = None
miner = None

# Dict of configuration parameters
token_retriever_account = "0x0F048ff7dE76B83fDC14912246AC4da5FA755cFE"
config = config_f('privateTestnet')
config['token_retriever_account'] = token_retriever_account
params = [config['multisig_owners'][0], config['startTime'], config['endTime'], config['token_retriever_account'], config['tranches']]
params_log_path = "./params_log"

# Get CrowdsaleToken ABI
with open("./build/CrowdsaleToken.abi") as token_abi_file:
	token_abi = json.load(token_abi_file)

# Display configuration parameters, confirm them, write them to json file
def dump():
	
	pending_input = True
	consent = None
	
	# Displaying configuration parameters ----------------------------------------------------------------------------------
	print("\n\nWeb3 version:", web3.version.api)
	
	print(
	  "\n\nMultisig address:", config['multisig_owners'][0], 
	  "\n\nStart time:", time.ctime(config['startTime']),
	  "\n\nEnd time:", time.ctime(config['endTime']),
	  "\n\nToken retriever: " + config['token_retriever_account']
	);
	
	for x in range(0,int((len(config['tranches'])/4)-1)):
		print("\n\nTranche #", x, " -----------------------------------------------------------------",
	    "\nFullTokens cap:", int(config['tranches'][4*x]/(10**18)),
	    "\nStart:         ", time.ctime(config['tranches'][4*x+1]),
	    "\nEnd:           ", time.ctime(config['tranches'][4*x+2]),
	    "\nTokens per EUR:", config['tranches'][4*x+3]
	  )
	
	print("------------------------------------------------------------------------------");
	print("\n\nTransaction sender: " + accounts[0],
	      "\nGas and Gas price: " + str(gas) + " and " + str(gas_price) + "\n"
	)
	
	# ----------------------------------------------------------------------------------------------------------------------
	
	# Validating configuration parameters
	while pending_input:
	
		consent = input('\nDo you agree with the information? [yes/no]: ')
	
		if consent == 'yes':
			pending_input = False
		elif consent == 'no':
			sys.exit("Aborted")
		else:
			print("\n\nPlease enter 'yes' or 'no'\n")
	
	deployment_name = input('\n\nEnter name of deployment: ')
	
	local_time = datetime.now()
	
	json_file_name = "Crowdsale" + '-' + local_time.strftime('%Y-%m-%d--%H-%M-%S') + '--' + deployment_name
	
	try:
		if not os.path.exists(params_log_path):
			os.makedirs(params_log_path)
	except OSError as e:
		if e.errno != errno.EEXIST:
			raise
	
	# Writing configuration parameters into json file for logging purposes
	file_path_name_w_ext = params_log_path + '/' + json_file_name + '.json'
	with open(file_path_name_w_ext, 'w') as fp:
		json.dump(config, fp, sort_keys=True, indent=4)

def configurate():
	testing.web3 = web3
	testing.accounts = accounts
	testing.params = params
	testing.crowdsale_contract = crowdsale_contract
	testing.configuration_crowdsale(params)
	testing.wait()
	token_address = testing.token()
	token_contract = web3.eth.contract(address=token_address, abi=token_abi)
	testing.token_contract = token_contract