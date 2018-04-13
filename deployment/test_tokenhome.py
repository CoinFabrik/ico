#!/usr/bin/env python3

import crowdsale_deployment
from configurate import config, sender_account
from crowdsale_checker import CrowdsaleChecker
import time

starting_time = int(round(time.time())) + 1
ending_time = int(round(time.time())) + 460

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
  halt_stage()
  require_customer_id_stage()

crowdsale_checker = CrowdsaleChecker(c)

all_checks_and_stages()

crowdsale_checker.try_configuration_crowdsale()

crowdsale_checker.try_set_starting_time(int(round(time.time())) + 3)
crowdsale_checker.start_ico()

crowdsale_checker.try_update_price_agent(sender_account)
crowdsale_checker.try_update_eurs_per_eth(3728700, sender_account)
crowdsale_checker.try_set_minimum_buy_value(0)

all_checks_and_stages()

crowdsale_checker.try_set_ending_time(int(round(time.time())) + 3)
crowdsale_checker.end_ico()

all_checks_and_stages()
