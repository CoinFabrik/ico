pragma solidity ^0.4.21;

import "./Ownable.sol";

contract StandardTokenMock2 is Ownable {
  function transfer(address to, uint value) public returns (bool success) {
    return true;
  }

  function transferFrom(address from, address to, uint value) public returns (bool success) {
    return true;
  }
}