import argparse

def get_args(args_list):
  parser = argparse.ArgumentParser()
  for arg in args_list:
    parser.add_argument("-" + arg[0][0], "--" + arg[0], action=arg[1], default=arg[2], help=arg[3])
  args = parser.parse_args()
  return args

args_list = [["network", None, "poanet", "Enter network, defaults to poanet"],
            ["provider", None, "http", "Enter provider, defaults to http"],
            ["address", None, None, "Enter address to look for log file"],
            ["deployment_name", None, None, "Enter deployment name to look for log file"],
            ["test", "store_true", False, "Testing mode"]]

args = get_args(args_list)