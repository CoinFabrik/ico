pragma solidity ^0.4.24;

import "./TokenTranchePricing.sol";

// TokenTranchePricing mock needed to expose some functions
contract TokenTranchePricingMock is TokenTranchePricing {

  function configurateTokenTranchePricingMock(uint[] init_tranches) public {
  	super.configurationTokenTranchePricing(init_tranches);
  }
}