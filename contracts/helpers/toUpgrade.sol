pragma solidity ^0.4.15;

import '../UpgradeAgent.sol';

// Mock class for testing of UpgradeableToken
contract toUpgrade is UpgradeAgent{
    
  function toUpgrade(uint value){
    originalSupply = value;
  }

  function upgradeFrom(address from, uint value) public{
    //Does nothing, can't fail
  }
}