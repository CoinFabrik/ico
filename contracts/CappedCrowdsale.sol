pragma solidity ^0.4.15;

import "./GenericCrowdsale.sol";


contract CappedCrowdsale is GenericCrowdsale {

  // The funding cannot exceed this cap; it may be set later on during the crowdsale
  uint public weiFundingCap = 0;

  // A new funding cap has been set
  event FundingCapSet(uint newFundingCap);


  /**
   * Allow the owner to set a funding cap on the crowdsale.
   * The new cap should be higher than the minimum funding goal.
   * 
   * @param newCap minimum target cap that may be relaxed if it was already broken.
   */
  function setFundingCap(uint newCap) public onlyOwner notFinished {
    weiFundingCap = relaxFundingCap(newCap, weiRaised);
    require(weiFundingCap >= minimumFundingGoal);
    FundingCapSet(weiFundingCap);
  }
}