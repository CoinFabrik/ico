pragma solidity ^0.4.14;

/**
 * Interface for defining crowdsale ceiling.
 */
contract CeilingStrategy {

  /** Interface declaration. */
  function isCeilingStrategy() public constant returns (bool) {
    return true;
  }

  /** Self check if all references are correctly set.
   *
   * Checks that ceiling strategy matches crowdsale parameters.
   */
  function isSane(address _crowdsale) public constant returns (bool) {
    return true;
  }

  /**
   * When somebody tries to buy tokens for X wei, calculate how many weis they are allowed to use.
   *
   *
   * @param _value - What is the value of the transaction sent in as wei.
   * @param _weiRaised - How much money has been raised so far.
   * @param _weiInvestedBySender - the investment made by the address that is sending the transaction.
   * @param _weiFundingCap - the caller's declared total cap. May be reinterpreted by the implementation of the CeilingStrategy.
   * @return Amount of wei the crowdsale can receive.
   */
  function weiAllowedToReceive(uint _value, uint _weiRaised, uint _weiInvestedBySender, uint _weiFundingCap) public constant returns (uint amount);

  function isCrowdsaleFull(uint _weiRaised, uint _weiFundingCap) public constant returns (bool);

  /**
   * Calculate a new cap if the provided one is not above the amount already raised.
   *
   *
   * @param _newCap - The potential new cap.
   * @param _weiRaised - How much money has been raised so far.
   * @return The adjusted cap.
   */
  function relaxFundingCap(uint _newCap, uint _weiRaised) public constant returns (uint);

}