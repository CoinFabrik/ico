pragma solidity ^0.4.8;

import "../zeppelinTokenMarket/token/ERC20.sol";

/**
 * A token that defines fractional units as decimals.
 */
contract FractionalERC20 is ERC20 {

  uint public decimals;

}
