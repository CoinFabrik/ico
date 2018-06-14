pragma solidity ^0.4.24;

import "../TokenTranchePricing.sol";

// TokenTranchePricing mock needed to expose some functions
contract TokenTranchePricingMock is TokenTranchePricing {

  function getCurrentPriceMock(uint tokensSold) public view returns (uint result) {
    return super.getCurrentPrice(tokensSold);
  }
}
