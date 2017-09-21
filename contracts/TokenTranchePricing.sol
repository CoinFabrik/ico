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

  /**
   * Define pricing schedule using tranches.
   */
  struct Tranche {
      // Amount in weis when this tranche becomes active
      uint amount;
      // How many tokens per wei you will get while this tranche is active
      uint price;
  }

  Tranche[] public tranches;

  /// @dev Contruction, creating a list of tranches
  /// @param init_tranches Raw array of ordered pairs: (start amount, price)
  function TokenTranchePricing(uint[] init_tranches) {
    // Need to have tuples, length check
    require(init_tranches.length % 2 == 0);

    uint highestAmount = 0;

    for (uint i = 0; i < init_tranches.length / 2; i++) {
      // No invalid steps
      require((i == 0) || (init_tranches[i * 2] > highestAmount));

      tranches[i].amount = init_tranches[i * 2];
      tranches[i].price = init_tranches[i * 2 + 1];

      highestAmount = tranches[i].amount;
    }

    // Last tranche price must be zero, terminating the crowdale
    require(tranches[tranches.length.sub(1)].price == 0);
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
    return tranches[tranches.length - 1];
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
    // TODO: If using an absurd amount of tranches, implement binary search.
    for (uint i = tranches.length - 1; i < tranches.length; i--) {
      if (tokensSold >= tranches[i].amount) {
        return tranches[i];
      }
    }
  }

  /// @dev Get the current price.
  /// @param tokensSold total amount of tokens sold, for calculating the current tranche
  /// @return The current price or 0 if we are outside tranche ranges
  function getCurrentPrice(uint tokensSold) public constant returns (uint result) {
    return getCurrentTranche(tokensSold).price;
  }

}