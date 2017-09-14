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
  function setFundingCap(uint newCap) internal onlyOwner notFinished {
    require(newCap >= minimumFundingGoal);
    weiFundingCap = newCap;
    FundingCapSet(weiFundingCap);
  }

  // We set an upper bound for the sold tokens by limiting ether raised
  function weiAllowedToReceive(uint tentativeAmount, address) internal constant returns (uint) {
    // Then, we check the funding cap
    if (weiFundingCap == 0) return tentativeAmount;
    uint total = tentativeAmount.add(weiRaised);
    if (total < weiFundingCap) return tentativeAmount;
    else return weiFundingCap.sub(weiRaised);
  }
}