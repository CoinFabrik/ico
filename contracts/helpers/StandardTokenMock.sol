pragma solidity ^0.4.15;

import '../StandardToken.sol';

// Mock class for StandardToken contract
contract StandardTokenMock is StandardToken {
  function mint(address receiver, uint amount) public {
    mintInternal(receiver, amount);
  }
}