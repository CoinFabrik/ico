pragma solidity ^0.4.15;

/**
 * Originally from https://github.com/TokenMarketNet/ico
 * Modified by https://www.coinfabrik.com/
 */

import "./Ownable.sol";
import "./SafeMath.sol";
import "./Mintable.sol";

/**
 * A public interface to increase the supply of a token.
 *
 * This allows uncapped crowdsale by dynamically increasing the supply when money pours in.
 * Only mint agents, usually contracts whitelisted by the owner, can mint new tokens.
 *
 */
contract MintableToken is Mintable, Ownable {

  using SafeMath for uint;

  bool public mintingFinished = false;

  /** List of agents that are allowed to create new tokens */
  mapping (address => bool) public mintAgents;

  event MintingAgentChanged(address addr, bool state);


  function MintableToken(uint initialSupply, address multisig, bool mintable) internal {
    require(multisig != address(0));
    // Cannot create a token without supply and no minting
    require(mintable || initialSupply != 0);
    // Create initially all balance on the team multisig
    if (initialSupply > 0)
      mintInternal(multisig, initialSupply);
    // No more new supply allowed after the token creation
    mintingFinished = !mintable;
  }

  /**
   * Create new tokens and allocate them to an address.
   *
   * Only callable by a mint agent (e.g. crowdsale contract).
   */
  function mint(address receiver, uint amount) onlyMintAgent canMint public {
    mintInternal(receiver, amount);
  }

  /**
   * Owner can allow a crowdsale contract to mint new tokens.
   */
  function setMintAgent(address addr, bool state) onlyOwner canMint public {
    mintAgents[addr] = state;
    MintingAgentChanged(addr, state);
  }

  modifier onlyMintAgent() {
    // Only mint agents are allowed to mint new tokens
    require(mintAgents[msg.sender]);
    _;
  }

  /** Make sure we are not done yet. */
  modifier canMint() {
    require(!mintingFinished);
    _;
  }
}