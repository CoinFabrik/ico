import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-n", "--network", default="poanet", help="Enter network, defaults to poanet")
parser.add_argument("-p", "--provider", default="http", help="Enter provider, defaults to http")
parser.add_argument("-t", "--test", action="store_true", help="Testing mode")
parser.add_argument("-a", "--address", help="Enter address to look for log file")
parser.add_argument("-d", "--deployment_name", help="Enter deployment name to look for log file")
args = parser.parse_args()