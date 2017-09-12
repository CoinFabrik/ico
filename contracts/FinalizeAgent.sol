pragma solidity ^0.4.15;

/**
 * Originally from https://github.com/TokenMarketNet/ico
 */

 import "./CrowdsaleToken.sol";

/**
 * Finalize agent defines what happens at the end of a succesful crowdsale.
 *
 * - Allocate tokens for founders, bounties and community
 * - Make tokens transferable
 * - etc.
 */
contract FinalizeAgent {

  function isFinalizeAgent() public constant returns(bool) {
    return true;
  }

  /** Return true if we can run finalizeCrowdsale() properly.
   *
   * This is a safety check function that doesn't allow crowdsale to begin
   * unless the finalizer has been set up properly.
   */
  function isSane(CrowdsaleToken token) public constant returns (bool);

  /** Called once by crowdsale finalize() if the sale was a success. */
  function finalizeCrowdsale(CrowdsaleToken token) public;

}