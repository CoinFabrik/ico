pragma solidity ^0.4.13;

/**
 * Originally from https://github.com/TokenMarketNet/ico
 */
 
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
   * @ param  {uint value} Buy-in value in wei.
   * @ param
   * @ param
   * @ param
   * @ param  {uint decimals} The decimals used by the token representation (e.g. given by FractionalERC20).
   */
  function calculatePrice(uint value, uint, uint, address, uint decimals) public constant returns (uint) {
    uint multiplier = 10 ** decimals;
    return value.mul(multiplier).div(oneTokenInWei);
  }

}