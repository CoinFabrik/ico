#!/usr/bin/env python3
class Investor:  
  address = None
  whitelisted = False
  customerId = None

  def __init__(self, address_param, whitelisted=False, customerId=None):
    self.address = address_param
    self.whitelisted = whitelisted
    self.customerId = customerId
  
  def whitelist(self):
    self.whitelisted = True

  def unwhitelist(self):
    self.whitelisted = False

  