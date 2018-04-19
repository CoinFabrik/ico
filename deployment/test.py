#!/usr/bin/env python3

import crowdsale_deployment
from configurate import config
from crowdsale_checker import CrowdsaleChecker

def general_check():
  crowdsale_checker.check_state()
  crowdsale_checker.try_buys()
  crowdsale_checker.try_finalize()
  crowdsale_checker.try_preallocate()

def require_customer_id_stage():
  print("----Require Customer ID Stage")
  crowdsale_checker.require_customer_id()
  general_check()
  crowdsale_checker.unrequire_customer_id()
  print("----End Require Customer ID Stage")

def halt_stage():
  print("--Halt Stage")
  crowdsale_checker.halt()
  general_check()
  require_customer_id_stage()
  crowdsale_checker.unhalt()
  print("--End Halt Stage")

def all_checks_and_stages():
  general_check()
  #halt_stage()
  #require_customer_id_stage()

crowdsale_checker = CrowdsaleChecker(config)

print("Pre-ICO before configuration stage")

all_checks_and_stages()

print("End Pre-ICO before configuration stage")

crowdsale_checker.try_configuration_crowdsale()

crowdsale_checker.set_early_participant_whitelist()

print("Pre-ico after configuration stage")

all_checks_and_stages()

crowdsale_checker.start_ico()

print("ICO Stage")

all_checks_and_stages()

crowdsale_checker.end_ico()

print("End ICO Stage")

all_checks_and_stages()

miner.stop()