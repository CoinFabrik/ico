pragma solidity ^0.4.21;

import "./GenericCrowdsale.sol";
import "./StandardTokenMock.sol";

contract GenericCrowdsaleMock is GenericCrowdsale {
  StandardTokenMock public token;
  uint public sellable_tokens;

  function GenericCrowdsaleMock() public {
    token = new StandardTokenMock();
  }

  function assignTokens(address receiver, uint tokenAmount) internal {
    token.transfer(receiver, tokenAmount);
  }

  function calculateTokenAmount(uint weiAmount, address receiver) internal view returns (uint weiAllowed, uint tokenAmount) {
    weiAllowed = 50000;
    tokenAmount = 100000;
  }

  function isCrowdsaleFull() internal view returns (bool full) {
    return tokensSold >= sellable_tokens;
  }
}