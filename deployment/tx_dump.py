import time
import json
import sys
from contract import Contract

def dump(web3, args, config, tx_args_dict):
  log_path = "./log/"
  # Displaying configuration parameters
  print("\nWeb3 version:", web3.version.api)
  print("\nWeb3 network:", args.network)
  print(
    "\n\nMultisig address:", config['MW_address'][0],
    "\n\nStart time:", time.asctime(time.gmtime(config['start_time'])) + " (GMT)",
    "\n\nEnd time:", time.asctime(time.gmtime(config['end_time'])) + " (GMT)",
    "\n\nToken retriever: " + config['token_retriever_account']
  );  
  for x in range(int(len(config['tranches'])/4)):
    print("\nTranche #", x, " -----------------------------------------------------------------",
      "\nFullTokens cap:", int(config['tranches'][4*x]/(10**18)),
      "\nStart:         ", time.asctime(time.gmtime(config['tranches'][4*x+1])) + " (GMT)",
      "\nEnd:           ", time.asctime(time.gmtime(config['tranches'][4*x+2])) + " (GMT)",
      "\nTokens per EUR:", config['tranches'][4*x+3]
    )  
  print("------------------------------------------------------------------------------");
  print("\nTransaction sender: ", tx_args_dict["from"],
        "\nGas and Gas price: ", tx_args_dict["gas"], " and ", tx_args_dict["gasPrice"], "\n"
  )  
  # Validating configuration parameters
  while True:
    consent = input('\nDo you agree with the information? [yes/no]: ')
    if consent == 'yes':
      break
    elif consent == 'no':
      sys.exit("Aborted")
    else:
      print("\nPlease enter 'yes' or 'no'\n")
  
  Contract.exists_folder(log_path)
  
  # Writing configuration parameters into json file for logging purposes
  (log_json, file_path) = Contract.get_deployment_json_and_path(log_path, deployment_name=args.deployment_name, address=args.address)
  log_json.update(config)
  with open(file_path, 'w') as fp:
    json.dump(log_json, fp, sort_keys=True, indent=2)