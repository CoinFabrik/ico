pragma solidity ^0.4.11;

import './StandardToken.sol';
import "./UpgradeableToken.sol";
import "./ReleasableToken.sol";
import "./UpgradeAgent.sol";
import "./Ownable.sol";


/**
 * An upgrade token.
 *
 * - The token contract gives an opt-in upgrade path to a new contract
 * - The totalSupply is fixed at creation
 * - The address(0) is allocated all tokens on creation
 * - Tokens will be transfered on upgrade
 *
 */
contract MysteriumToken is UpgradeableToken, UpgradeAgent, Ownable {

  string public name;

  string public symbol;

  uint public decimals;

  /** We only accept upgrades from this address */
  address public originaryToken;

  modifier onlyOriginaryToken () {
    if (msg.sender != originaryToken) {
      throw;
    }
    _;
  }

  /**
   * Construct the token.
   */
  function MysteriumToken(string _name, string _symbol, uint _totalSupply, uint _decimals)
    UpgradeableToken(msg.sender) {

    owner = msg.sender;

    name = _name;
    symbol = _symbol;

    totalSupply = _totalSupply;
    originalSupply = _totalSupply;

    decimals = _decimals;

    // address(0) has all the tokens
    balances[address(0)] = totalSupply;

    if (totalSupply == 0) {
      throw;
    }

    Minted(address(0), totalSupply);
  }

  /**
   * Owner can set originary token
   */
  function setOriginaryToken(address _originaryToken) onlyOwner {
    originaryToken = _originaryToken;
  }

  /**
   * Only upgrade client can upgrade tokens
   */
  function upgradeFrom(address _from, uint256 _value) public onlyOriginaryToken {
    balances[address(0)] = balances[address(0)].sub(_value);
    balances[_from] = balances[_from].add(_value);
    Transfer(address(0), _from, _value);
  }
}
