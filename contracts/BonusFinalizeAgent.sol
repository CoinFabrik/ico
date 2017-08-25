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
contract BonusFinalizeAgent is FinalizeAgent {

  using SafeMath for uint;

  Crowdsale public crowdsale;

  /** Total percent of tokens minted to the team at the end of the sale as base points
  bonus tokens = tokensSold * bonusBasePoints * 0.0001         */
  uint public bonusBasePoints;

  /** Implementation detail. This is the divisor of the base points **/
  uint private constant basePointsDivisor = 10000;

  /** Where we move the tokens at the end of the sale. */
  address public teamMultisig;

  /* How many bonus tokens we allocated */
  uint public allocatedBonus;

  function BonusFinalizeAgent(Crowdsale _crowdsale, uint _bonusBasePoints, address _teamMultisig) {
    require(address(_crowdsale) != 0 && address(_teamMultisig) != 0);
    crowdsale = _crowdsale;
    teamMultisig = _teamMultisig;
    bonusBasePoints = _bonusBasePoints;
  }

  /* Can we run finalize properly */
  function isSane(HagglinToken token) public constant returns (bool) {
    return token.mintAgents(address(this)) && token.releaseAgent() == address(this);
  }

  /** Called once by crowdsale finalize() if the sale was a success. */
  function finalizeCrowdsale(HagglinToken token) {
    require(msg.sender == address(crowdsale));

    // How many % points of tokens the founders and others get
    uint tokensSold = crowdsale.tokensSold();
    uint saleBasePoints = basePointsDivisor.sub(bonusBasePoints);
    allocatedBonus = tokensSold.mul(bonusBasePoints).div(saleBasePoints);

    // Move tokens to the team multisig wallet
    token.mint(teamMultisig, allocatedBonus);

    // Make token transferable
    token.releaseTokenTransfer();
  }

}