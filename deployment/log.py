from contract import Contract
from datetime import datetime
import json

def log_address(contract):
  """Write contract's address to json file in log directory."""
  log_path = "./log/"
  Contract.exists_folder(log_path)
  deployment_name = input("Enter a name for the deployment: ")
  local_time = datetime.now()
  json_file_name = deployment_name + '--' + local_time.strftime('%Y-%m-%d--%H-%M-%S') + "--" + contract.address
  file_path_name_w_ext = log_path + json_file_name + '.json'
  address_dict = {'contract_address': contract.address, 'deployment_name': deployment_name}
  with open(file_path_name_w_ext, 'w') as fp:
    json.dump(address_dict, fp, sort_keys=True, indent=2)