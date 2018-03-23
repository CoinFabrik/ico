#!/usr/bin/env python3



class Investor:
  
  address = None
  whitelisted = False
  customerId = None

  def __init__(self, address_param):
    self.address = address_param
  
  def whitelist(self):
    self.whitelisted = True

  def unwhitelist(self):
    self.whitelisted = False

  