pragma solidity ^0.4.11;

import "./Crowdsale.sol";
import "./CrowdsaleToken.sol";
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

  CrowdsaleToken public token;
  Crowdsale public crowdsale;

  /** Total percent of tokens minted to the team at the end of the sale as base points (0.0001) */
  uint public bonusBasePoints;

  /** Where we move the tokens at the end of the sale. */
  address public teamMultisig;

  /* How many bonus tokens we allocated */
  uint public allocatedBonus;

  function BonusFinalizeAgent(CrowdsaleToken _token, Crowdsale _crowdsale, uint _bonusBasePoints, address _teamMultisig) {
    require(address(_token) != 0 && address(_crowdsale) != 0 && address(_teamMultisig) != 0);
    token = _token;
    crowdsale = _crowdsale;
    teamMultisig = _teamMultisig;
    bonusBasePoints = _bonusBasePoints;
  }

  /* Can we run finalize properly */
  function isSane() public constant returns (bool) {
    return (token.mintAgents(address(this)) == true) && (token.releaseAgent() == address(this));
  }

  /** Called once by crowdsale finalize() if the sale was a success. */
  function finalizeCrowdsale() {
    require(msg.sender == address(crowdsale));

    // How many % of tokens the founders and others get
    uint tokensSold = crowdsale.tokensSold();
    allocatedBonus = tokensSold.mul(bonusBasePoints) / 10000;

    // Move tokens to the team multisig wallet
    token.mint(teamMultisig, allocatedBonus);

    // Make token transferable
    token.releaseTokenTransfer();
  }

}