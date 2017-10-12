pragma solidity ^0.4.15;

import '../UpgradeableToken.sol';
import '../BasicToken.sol';

// Mock class for testing of UpgradeableToken
contract toBeUpgraded is UpgradeableToken, BasicToken {
    
  bool canUp;

  //constructor
  function toBeUpgraded(uint value) public
  UpgradeableToken(msg.sender){
    mintInternal(msg.sender, value);
    setCanUp(true);
  }

  function setCanUp(bool value) public{
    canUp = value;
  }

  //Blocked to avoid change of tokens amount except from upgrading
  function transfer(address to, uint value) public returns (bool success) {
    return true;
  }


  /**
   * Overriden for testing different values
   */
  function canUpgrade() public constant returns(bool) {
     return canUp;
  }
}
