#!/usr/bin/env python3

import crowdsale_deployment
from set_config import params
from crowdsale_checker import CrowdsaleChecker

def general_check():
  crowdsale_checker.check_state()
  crowdsale_checker.try_buys()
  crowdsale_checker.try_finalize()
  crowdsale_checker.try_preallocate()

def require_customer_id_stage():
  crowdsale_checker.require_customer_id()
  general_check()
  crowdsale_checker.unrequire_customer_id()


crowdsale_checker = CrowdsaleChecker(params)

# Pre-ico before configuration stage --------------------------------------------------------

general_check()

# -- Halt stage

crowdsale_checker.halt()

general_check()

# ---- Require Customer ID stage

require_customer_id_stage()

# ---- End Require Customer ID stage

crowdsale_checker.unhalt()

# -- End Halt stage

# -- Require Customer ID stage

require_customer_id_stage()

# -- End Require Customer ID stage

# End Pre-ico before configuration stage -----------------------------------------------

crowdsale_checker.try_configuration_crowdsale()

crowdsale_checker.set_early_participant_whitelist()

# Pre-ico after configuration stage ---------------------------------------------------------

general_check()

# -- Halt stage

crowdsale_checker.halt()

general_check()

# ---- Require Customer ID stage

require_customer_id_stage()

# ---- End Require Customer ID stage

crowdsale_checker.unhalt()

# -- End Halt stage

# -- Require Customer ID stage

require_customer_id_stage()

# -- End Require Customer ID stage

crowdsale_checker.start_ico()

# ICO stage ---------------------------------------------------------------------------------

general_check()

# -- Halt stage

crowdsale_checker.halt()

general_check()

# ---- Require Customer ID stage

require_customer_id_stage()

# ---- End Require Customer ID stage

crowdsale_checker.unhalt()

# -- End Halt stage

# -- Require Customer ID stage

require_customer_id_stage()

# -- End Require Customer ID stage

crowdsale_checker.end_ico()

# End ICO stage -----------------------------------------------------------------------------

general_check()

# -- Halt stage

crowdsale_checker.halt()

general_check()

# ---- Require Customer ID stage

require_customer_id_stage()

# ---- End Require Customer ID stage

crowdsale_checker.unhalt()

# -- End Halt stage

# -- Require Customer ID stage

require_customer_id_stage()

# -- End Require Customer ID stage

miner.stop()