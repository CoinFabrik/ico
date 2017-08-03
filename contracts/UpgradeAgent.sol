pragma solidity ^0.4.14;

/**
 * Inspired by Lunyr.
 * Originally from https://github.com/TokenMarketNet/ico
 */

/**
 * Upgrade agent transfers tokens to a new contract.
 * Upgrade agent itself can be the token contract, or just a middle man contract doing the heavy lifting.
 *
 */
contract UpgradeAgent {

  uint public originalSupply;

  /** Interface marker */
  function isUpgradeAgent() public constant returns (bool) {
    return true;
  }

  function upgradeFrom(address _from, uint _value) public;

}
