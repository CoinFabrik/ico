pragma solidity ^0.4.15;

/**
 * Originally from https://github.com/TokenMarketNet/ico
 * Modified by https://www.coinfabrik.com/
 */

import "./Ownable.sol";
import './StandardToken.sol';
import "./SafeMath.sol";

/**
 * A token that can increase its supply by another contract.
 *
 * This allows uncapped crowdsale by dynamically increasing the supply when money pours in.
 * Only mint agents, contracts whitelisted by owner, can mint new tokens.
 *
 */
contract MintableToken is StandardToken, Ownable {

  using SafeMath for uint;

  bool public mintingFinished = false;

  /** List of agents that are allowed to create new tokens */
  mapping (address => bool) public mintAgents;

  event MintingAgentChanged(address addr, bool state);


  function MintableToken(uint _initialSupply, address _multisig, bool _mintable) internal {
    require(_multisig != address(0));
    // Cannot create a token without supply and no minting
    require(_mintable || _initialSupply != 0);
    // Create initially all balance on the team multisig
    if (_initialSupply > 0)
        mintInternal(_multisig, _initialSupply);
    // No more new supply allowed after the token creation
    mintingFinished = !_mintable;
  }

  /**
   * Create new tokens and allocate them to an address.
   *
   * Only callable by a crowdsale contract (mint agent).
   */
  function mint(address receiver, uint amount) onlyMintAgent public {
    mintInternal(receiver, amount);
  }

  function mintInternal(address receiver, uint amount) canMint private {
    totalSupply = totalSupply.add(amount);
    balances[receiver] = balances[receiver].add(amount);

    // Removed because this may be confused with anonymous transfers in the upcoming fork.
    // This will make the mint transaction appear in EtherScan.io
    // We can remove this after there is a standardized minting event
    // Transfer(0, receiver, amount);

    Minted(receiver, amount);
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