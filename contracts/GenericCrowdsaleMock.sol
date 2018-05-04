pragma solidity ^0.4.23;

import "./GenericCrowdsale.sol";
import "./StandardTokenMock.sol";

contract GenericCrowdsaleMock is GenericCrowdsale {
  StandardTokenMock public token;
  uint public sellable_tokens;

  constructor() public {
    token = new StandardTokenMock();
  }

  function configuration(address team_multisig, uint start, uint end) public {
    super.configurationGenericCrowdsale(team_multisig, start, end);
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