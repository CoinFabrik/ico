pragma solidity ^0.4.18;

import "./SafeMath.sol";

// TokenTranchePricing mock needed to expose some functions
contract TokenTranchePricingMock {
   function getCurrentPrice(uint tokensSold) public view returns (uint result) {
    return super.getCurrentPrice(tokensSold);
  }
}
