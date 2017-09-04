pragma solidity ^0.4.13;

contract RevenueStrategy {
  /** Interface declaration. */
  function isRevenueStrategy() public constant returns (bool) {
    return true;
  }

  function revenuePerPayday() public constant returns (uint);
}