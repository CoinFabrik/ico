pragma solidity ^0.4.23;

import '../UpgradeableToken.sol';
import '../StandardToken.sol';

// Mock class for testing of UpgradeableToken
contract toBeUpgraded is UpgradeableToken, StandardToken {
    
  bool public canUp;

  //constructor
  constructor(uint value) public
  UpgradeableToken(msg.sender) {
    mintInternal(msg.sender, value);
    setCanUp(true);
  }

  function setCanUp(bool value) public {
    canUp = value;
  }

  //Blocked to avoid change of tokens amount except from upgrading
  function transfer(address, uint) public returns (bool) {
    return true;
  }


  /**
   * Overriden for testing different values
   */
  function canUpgrade() public view returns(bool) {
     return canUp;
  }
}
