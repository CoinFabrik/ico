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
   * When somebody tries to buy tokens for X eth, calculate how many eths they are allowed to use.
   *
   *
   * @param value - What is the value of the transaction send in as wei
   * @param weiRaised - how much money has been raised this far
   * @param msgSender - who is the investor of this transaction
   * @return Amount of eth the investor can send
   */
  function ethAllowedToSend(uint _value, uint _weiRaised, address _msgSender) public constant returns (uint amount);

}