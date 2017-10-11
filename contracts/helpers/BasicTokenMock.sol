pragma solidity ^0.4.15;

import '../BasicToken.sol';

// Mock class for BasicToken contract
contract BasicTokenMock is BasicToken {
  
  /**
   * Made public for abvailability in tests
   */
  function burnTokensMock(address account, uint value) public {
    super.burnTokens(account, value);
  }

  /**
   * @dev Made public for abvailability in tests
   */
  function mintInternalMock(address receiver, uint amount) public {
    super.mintInternal(receiver, amount);
  }
  
}