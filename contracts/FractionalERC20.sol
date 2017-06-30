pragma solidity ^0.4.11;

/**
 * Originally from https://github.com/TokenMarketNet/ico
 */

import "./ERC20.sol";

/**
 * A token that defines fractional units as decimals.
 */
contract FractionalERC20 is ERC20 {

  uint public decimals;

}