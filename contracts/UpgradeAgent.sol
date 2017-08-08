pragma solidity ^0.4.13;

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

  /** This value should be the same as the original token's total supply */
  uint public originalSupply;

  /** Interface marker */
  function isUpgradeAgent() public constant returns (bool) {
    return true;
  }

  /** This function is called by the old token to inform the new token contract that the address _from is upgrading _value tokens */
  function upgradeFrom(address _from, uint _value) public;

}
