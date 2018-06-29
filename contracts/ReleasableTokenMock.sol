pragma solidity ^0.4.24;

import "./ReleasableToken.sol";

contract ReleasableTokenMock is ReleasableToken {

  function mint(address receiver, uint amount) public onlyOwner {
    mintInternal(receiver, amount);
  }
}