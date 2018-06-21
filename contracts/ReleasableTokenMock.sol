pragma solidity ^0.4.23;

import "./ReleasableToken.sol";

contract ReleasableTokenMock is ReleasableToken {

  function mint(address receiver, uint amount) public onlyOwner {
    mintInternal(receiver, amount);
  }
}