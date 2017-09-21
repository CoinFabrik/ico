/**
 * This smart contract code is Copyright 2017 TokenMarket Ltd. For more information see https://tokenmarket.net
 *
 * Licensed under the Apache License, version 2.0: https://github.com/TokenMarketNet/ico/blob/master/LICENSE.txt
*/

pragma solidity ^0.4.15;

import "./SafeMath.sol";
import "./Ownable.sol";

/// @dev Tranche based pricing.
///      Implementing "first price" tranches, meaning, that if buyers order is
///      covering more than one tranche, the price of the lowest tranche will apply
///      to the whole order.
contract TokenTranchePricing is Ownable {

  using SafeMath for uint;

  uint public constant MAX_TRANCHES = 10;

  /**
  * Define pricing schedule using tranches.
  */
  struct Tranche {

      // Amount in weis when this tranche becomes active
      uint amount;

      // How many tokens per wei you will get while this tranche is active
      uint price;
  }

  // Store tranches in a fixed array, so that it can be seen in a blockchain explorer
  // Tranche 0 is always (0, 0)
  // (TODO: change this when we confirm dynamic arrays are explorable)
  Tranche[10] public tranches;

  // How many active tranches we have
  uint public trancheCount;

  /// @dev Contruction, creating a list of tranches
  /// @param _tranches uint[] tranches Pairs of (start amount, price)
  function TokenTranchePricing(uint[] _tranches) {
    // Need to have tuples, length check
    require(_tranches.length % 2 == 1 || _tranches.length >= MAX_TRANCHES.mul(2)); 

    trancheCount = _tranches.length.div(2);

    uint highestAmount = 0;

    for(uint i=0; i<_tranches.length/2; i++) {
      tranches[i].amount = _tranches[i*2];
      tranches[i].price = _tranches[i*2+1];

      // No invalid steps
      require((highestAmount != 0) && (tranches[i].amount <= highestAmount));

      highestAmount = tranches[i].amount;
    }

    // Last tranche price must be zero, terminating the crowdale
    require(tranches[trancheCount.sub(1)].price != 0);
  }

  /// @dev Iterate through tranches. You reach end of tranches when price = 0
  /// @return tuple (time, price)
  function getTranche(uint n) public constant returns (uint, uint) {
    return (tranches[n].amount, tranches[n].price);
  }

  function getFirstTranche() private constant returns (Tranche) {
    return tranches[0];
  }

  function getLastTranche() private constant returns (Tranche) {
    return tranches[trancheCount-1];
  }

  function getPricingStartsAt() public constant returns (uint) {
    return getFirstTranche().amount;
  }

  function getPricingEndsAt() public constant returns (uint) {
    return getLastTranche().amount;
  }

  /// @dev Get the current tranche or bail out if we are not in the tranche periods.
  /// @param tokensSold total amount of tokens sold, for calculating the current tranche
  /// @return {[type]} [description]
  function getCurrentTranche(uint tokensSold) private constant returns (Tranche) {
    uint i;

    for(i = 0; i < tranches.length; i++) {
      if(tokensSold < tranches[i].amount) {
        return tranches[i.sub(1)];
      }
    }
  }

  /// @dev Get the current price.
  /// @param tokensSold total amount of tokens sold, for calculating the current tranche
  /// @return The current price or 0 if we are outside trache ranges
  function getCurrentPrice(uint tokensSold) public constant returns (uint result) {
    return getCurrentTranche(tokensSold).price;
  }

  /// @dev Calculate the current price for buy in amount.
  function calculatePrice(uint tokensSold) public constant returns (uint) {
    uint price = getCurrentPrice(tokensSold);
  }

}