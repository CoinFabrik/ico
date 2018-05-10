#!/usr/bin/env python3

import sys
sys.path.append("../deployment")
from crowdsale_checker import CrowdsaleChecker

class GenericCrowdsaleChecker(CrowdsaleChecker):

  def __init__(self, params, contract_name, token_contract_name, addr_path=None, contract_addr=None):
    CrowdsaleChecker.__init__(self, params, contract_name, token_contract_name, addr_path=addr_path, contract_addr=contract_addr)

  def calculate_token_amount():
    pass
