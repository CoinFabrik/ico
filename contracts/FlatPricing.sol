pragma solidity ^0.4.13;

/**
 * Originally from https://github.com/TokenMarketNet/ico
 */

import "./Crowdsale.sol";
import "./PricingStrategy.sol";
import "./SafeMath.sol";

/**
 * Fixed crowdsale pricing - everybody gets the same price.
 */
contract FlatPricing is PricingStrategy {

  using SafeMath for uint;

  /* How many weis one token costs */
  uint public oneTokenInWei;

  function FlatPricing(uint _oneTokenInWei) {
    oneTokenInWei = _oneTokenInWei;
  }

  /**
   * Calculate the current price for buy in amount.
   *
   * @ param  {uint amount} Buy-in value in wei.
   */
  function calculatePrice(uint value, uint, uint, address, uint decimals) public constant returns (uint) {
    uint multiplier = 10 ** decimals;
    return value.mul(multiplier) / oneTokenInWei;
  }

}