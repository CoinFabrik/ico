pragma solidity ^0.4.24;

import './StandardToken.sol';

// Mock class for StandardToken contract
contract StandardTokenMock is StandardToken {
  function mint(address receiver, uint amount) public {
    mintInternal(receiver, amount);
  }
  
  /**
   * Made public for availability in tests
   */
  function burnTokensMock(address account, uint value) public {
    super.burnTokens(account, value);
  }
}