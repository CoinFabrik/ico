pragma solidity ^0.4.23;

import './UpgradeAgent.sol';

// Mock class for testing of UpgradeableToken
contract UpgradeAgentMock is UpgradeAgent {
    
  constructor(uint value) public {
    originalSupply = value;
  }

  function upgradeFrom(address, uint) public {
    //Does nothing, can't fail
  }
}