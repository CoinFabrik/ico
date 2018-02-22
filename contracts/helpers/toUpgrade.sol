pragma solidity ^0.4.20;

import '../UpgradeAgent.sol';

// Mock class for testing of UpgradeableToken
contract toUpgrade is UpgradeAgent {
    
  function toUpgrade(uint value) public {
    originalSupply = value;
  }

  function upgradeFrom(address, uint) public {
    //Does nothing, can't fail
  }
}