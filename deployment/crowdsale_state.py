#!/usr/bin/env python3

states = {"Unknown": 0, "PendingConfiguration": 1, "PreFunding": 2, "Funding": 3, "Success": 4, "Finalized": 5}

class CrowdsaleState:
  
  requiredCustomerId = False
  requiredSignedAddress = False
  halted = False
  state = None
  signer = None

  def __init__(self):
    self.state = states["Unknown"]

  def requireCustomerId(self):
    self.requiredCustomerId = True

  def unrequireCustomerId(self):
    self.requiredCustomerId = False

  def requireSignedAddress(self, signer):
    self.signer = signer
    self.requiredSignedAddress = True

  def unrequireSignedAddress(self, signer):
    self.signer = signer
    self.requiredSignedAddress = False

  def halt(self):
    self.halted = True

  def unhalt(self):
    self.halted = False