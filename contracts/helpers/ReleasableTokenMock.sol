pragma solidity ^0.4.15;

import '../ReleasableToken.sol';

// Mock class for ReleasableToken contract
contract ReleasableTokenMock is ReleasableToken {

  /**
   * Made public for abvailability in tests
   */
  function mint(address receiver, uint amount) public {
    super.mintInternal(receiver, amount);
  }
}