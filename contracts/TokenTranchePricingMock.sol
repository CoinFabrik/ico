pragma solidity ^0.4.21;

import "./TokenTranchePricing.sol";

// TokenTranchePricing mock needed to expose some functions
contract TokenTranchePricingMock is TokenTranchePricing {

  function getCurrentPriceMock(uint tokensSold) public view returns (uint result) {
    return super.getCurrentPrice(tokensSold);
  }

  function configurateTokenTranchePricingMock(uint[] init_tranches) public {
  	super.configurationTokenTranchePricing(init_tranches);
  }
}