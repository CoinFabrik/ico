pragma solidity ^0.4.11;

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
   * @param _value - What is the value of the transaction send in as wei.
   * @param _weiRaised - How much money has been raised so far.
   * @return Amount of wei the crowdsale can receive.
   */
  function weiAllowedToReceive(uint _value, uint _weiRaised) public constant returns (uint amount);

  function isCrowdsaleFull(uint _weiRaised) public constant returns (bool);

}