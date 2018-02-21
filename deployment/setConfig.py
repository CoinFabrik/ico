from config import config_f
import testing

tokenRetrieverAccount = "0x0F048ff7dE76B83fDC14912246AC4da5FA755cFE"

# Dict of configuration parameters
config = config_f('privateTestnet')
config['tokenRetrieverAccount'] = tokenRetrieverAccount
params = [config['multisig_owners'][0], config['startTime'], config['endTime'], config['tokenRetrieverAccount'], config['tranches']]

# Get CrowdsaleToken ABI
with open("./build/CrowdsaleToken.abi") as token_abi_file:
	token_abi = json.load(token_abi_file)

# Displaying configuration parameters ----------------------------------------------------------------------------------

print("\n\nWeb3 version:", web3.version.api)

print(
  "\n\nMultisig address:", config['multisig_owners'][0], 
  "\n\nStart time:", time.ctime(config['startTime']),
  "\n\nEnd time:", time.ctime(config['endTime']),
  "\n\nToken retriever: " + tokenRetrieverAccount
);

for x in range(0,int((len(config['tranches'])/4)-1)):
	print("\n\nTranche #", x, " -----------------------------------------------------------------",
    "\nFullTokens cap:", int(config['tranches'][4*x]/(10**18)),
    "\nStart:         ", time.ctime(config['tranches'][4*x+1]),
    "\nEnd:           ", time.ctime(config['tranches'][4*x+2]),
    "\nTokens per EUR:", config['tranches'][4*x+3]
  )

print("------------------------------------------------------------------------------");
print("\n\nTransaction sender: " + firstAccount,
      "\nGas and Gas price: " + str(gas) + " and " + str(gasPrice) + "\n"
)

# ----------------------------------------------------------------------------------------------------------------------


# Validating configuration parameters

while pendingInput:

	consent = input('\nDo you agree with the information? [yes/no]: ')

	if consent == 'yes':
		pendingInput = False
	elif consent == 'no':
		sys.exit("Aborted")
	else:
		print("\n\nPlease enter 'yes' or 'no'\n")

deployName = input('\n\nEnter name of deployment: ')

localTime = datetime.now()

jsonFileName = "Crowdsale" + '-' + localTime.strftime('%Y-%m-%d--%H-%M-%S') + '--' + deployName

try:
	if not os.path.exists(paramsLogPath):
		os.makedirs(paramsLogPath)
except OSError as e:
	if e.errno != errno.EEXIST:
		raise

# Writing configuration parameters into json file for logging purposes
writeToJSONFile(paramsLogPath, jsonFileName, config)


testing.configurate(params)

testing.wait()

tokenAddress = crowdsale_contract.functions.token().call()

token_contract = web3.eth.contract(address=tokenAddress, abi=token_abi)
testing.tokenContract = token_contract





