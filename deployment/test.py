#!/usr/bin/env python3

import deploy
from setConfig import wait, dump, time, params, miner, accounts, web3
from crowdsale_checker import CrowdsaleChecker


crowdsale_checker = CrowdsaleChecker(params)

# Pre-ico before configuration stage --------------------------------------------------------

crowdsale_checker.check_state()

crowdsale_checker.try_buys()

crowdsale_checker.try_finalize()

crowdsale_checker.try_preallocate()

# -- Halt stage

crowdsale_checker.halt()

crowdsale_checker.check_state()

crowdsale_checker.try_buys()

crowdsale_checker.try_finalize()

crowdsale_checker.try_preallocate()

# ---- Require Customer ID stage

crowdsale_checker.require_customer_id()

crowdsale_checker.check_state()

crowdsale_checker.try_buys()

crowdsale_checker.try_finalize()

crowdsale_checker.try_preallocate()

crowdsale_checker.unrequire_customer_id()

# ---- End Require Customer ID stage

crowdsale_checker.unhalt()

# -- End Halt stage

# -- Require Customer ID stage

crowdsale_checker.require_customer_id()

crowdsale_checker.check_state()

crowdsale_checker.try_buys()

crowdsale_checker.try_finalize()

crowdsale_checker.try_preallocate()

crowdsale_checker.unrequire_customer_id()

# -- End Require Customer ID stage

# End Pre-ico before configuration stage -----------------------------------------------

crowdsale_checker.try_configuration_crowdsale()

# Pre-ico after configuration stage ---------------------------------------------------------

crowdsale_checker.check_state()

crowdsale_checker.try_buys()

crowdsale_checker.try_finalize()

crowdsale_checker.try_preallocate()

# -- Halt stage

crowdsale_checker.halt()

crowdsale_checker.check_state()

crowdsale_checker.try_buys()

crowdsale_checker.try_finalize()

crowdsale_checker.try_preallocate()

# ---- Require Customer ID stage

crowdsale_checker.require_customer_id()

crowdsale_checker.check_state()

crowdsale_checker.try_buys()

crowdsale_checker.try_finalize()

crowdsale_checker.try_preallocate()

crowdsale_checker.unrequire_customer_id()

# ---- End Require Customer ID stage

crowdsale_checker.unhalt()

# -- End Halt stage

# -- Require Customer ID stage

crowdsale_checker.require_customer_id()

crowdsale_checker.check_state()

crowdsale_checker.try_buys()

crowdsale_checker.try_finalize()

crowdsale_checker.try_preallocate()

crowdsale_checker.unrequire_customer_id()

# -- End Require Customer ID stage

crowdsale_checker.start_ico()

# ICO stage ---------------------------------------------------------------------------------

crowdsale_checker.check_state()

crowdsale_checker.try_buys()

crowdsale_checker.try_finalize()

crowdsale_checker.try_preallocate()

# -- Halt stage

crowdsale_checker.halt()

crowdsale_checker.check_state()

crowdsale_checker.try_buys()

crowdsale_checker.try_finalize()

crowdsale_checker.try_preallocate()

# ---- Require Customer ID stage

crowdsale_checker.require_customer_id()

crowdsale_checker.check_state()

crowdsale_checker.try_buys()

crowdsale_checker.try_finalize()

crowdsale_checker.try_preallocate()

crowdsale_checker.unrequire_customer_id()

# ---- End Require Customer ID stage

crowdsale_checker.unhalt()

# -- End Halt stage

# -- Require Customer ID stage

crowdsale_checker.require_customer_id()

crowdsale_checker.check_state()

crowdsale_checker.try_buys()

crowdsale_checker.try_finalize()

crowdsale_checker.try_preallocate()

crowdsale_checker.unrequire_customer_id()

# -- End Require Customer ID stage

crowdsale_checker.end_ico()

# End ICO stage -----------------------------------------------------------------------------

crowdsale_checker.check_state()

crowdsale_checker.try_buys()

crowdsale_checker.try_finalize()

crowdsale_checker.try_preallocate()

# -- Halt stage

crowdsale_checker.halt()

crowdsale_checker.check_state()

crowdsale_checker.try_buys()

crowdsale_checker.try_finalize()

crowdsale_checker.try_preallocate()

# ---- Require Customer ID stage

crowdsale_checker.require_customer_id()

crowdsale_checker.check_state()

crowdsale_checker.try_buys()

crowdsale_checker.try_finalize()

crowdsale_checker.try_preallocate()

crowdsale_checker.unrequire_customer_id()

# ---- End Require Customer ID stage

crowdsale_checker.unhalt()

# -- End Halt stage

# -- Require Customer ID stage

crowdsale_checker.require_customer_id()

crowdsale_checker.check_state()

crowdsale_checker.try_buys()

crowdsale_checker.try_finalize()

crowdsale_checker.try_preallocate()

crowdsale_checker.unrequire_customer_id()

# -- End Require Customer ID stage

miner.stop()