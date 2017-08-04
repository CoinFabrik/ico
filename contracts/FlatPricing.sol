pragma solidity ^0.4.14;

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

  /* How many decimal tokens one wei affords */
  uint public decimalTokensPerWei;

  function FlatPricing(uint _decimalTokensPerWei) {
    decimalTokensPerWei = _decimalTokensPerWei;
  }

  function isSane(Crowdsale crowdsale) public constant returns (bool) {
     return address(crowdsale.pricingStrategy()) == address(this);
  }

  /**
   * Calculate the current price for buy in amount.
   *
   * @ param  {uint amount} Buy-in value in wei.
   */
  function calculatePrice(uint value, uint, uint, address, uint) public constant returns (uint) {
    return value.mul(decimalTokensPerWei);
  }

}