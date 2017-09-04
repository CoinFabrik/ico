pragma solidity ^0.4.13;

/**
 * Originally from https://github.com/TokenMarketNet/ico
 * Modified by https://www.coinfabrik.com/
 */
 
import "./FinalizeAgent.sol";
import "./Crowdsale.sol";
import "./HagglinToken.sol";
import "./SafeMath.sol";

/**
 * At the end of the successful crowdsale allocate % bonus of tokens to the team.
 *
 * Unlock tokens.
 *
 * BonusAllocationFinal must be set as the minting agent for the MintableToken.
 *
 */
contract StandardFinalizeAgent is FinalizeAgent {

  using SafeMath for uint;

  Crowdsale public crowdsale;

  function StandardFinalizeAgent(Crowdsale _crowdsale) {
    require(address(_crowdsale) != 0);
    crowdsale = _crowdsale;
  }

  /* Can we run finalize properly */
  function isSane(HagglinToken token) public constant returns (bool) {
    return token.releaseAgent() == address(this);
  }

  /** Called once by crowdsale finalize() if the sale was a success. */
  function finalizeCrowdsale(HagglinToken token) {
    // Make token transferable
    token.releaseTokenTransfer();
  }

}