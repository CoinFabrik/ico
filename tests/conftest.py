#!/usr/bin/env python3

import pytest
import sys
sys.path.append("../deployment")
from web3_interface import Web3Interface


@pytest.fixture(scope="module")
def web3():
  return Web3Interface().w3