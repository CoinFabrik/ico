pragma solidity ^0.4.11;

import './StandardToken.sol';
import "./UpgradeableToken.sol";
import "./ReleasableToken.sol";
import "./UpgradeAgent.sol";


/**
 * A crowdsaled token.
 *
 * An ERC-20 token designed specifically for crowdsales with investor protection and further development path.
 *
 * - The token transfer() is disabled until the crowdsale is over
 * - The token contract gives an opt-in upgrade path to a new contract
 * - The same token can be part of several crowdsales through approve() mechanism
 * - The token can be capped (supply set in the constructor) or uncapped (crowdsale contract can mint new tokens)
 *
 */
contract MysteriumToken is ReleasableToken, UpgradeableToken {

  event UpdatedTokenInformation(string newName, string newSymbol);

  string public name;

  string public symbol;

  uint public decimals;

  /** We only accept upgrades from this address */
  UpgradeAgent public upgradeClient;

  modifier onlyUpgradeClient () {
    if (msg.sender != address(upgradeClient)) {
      throw;
    }
    _;
  }

  /**
   * Construct the token.
   *
   * This token must be created through a team multisig wallet, so that it is owned by that wallet.
   */
  function MysteriumToken(string _name, string _symbol, uint _initialSupply, uint _decimals)
    UpgradeableToken(msg.sender) {

    owner = msg.sender;

    name = _name;
    symbol = _symbol;

    totalSupply = _initialSupply;

    decimals = _decimals;

    // address(0) has all the tokens
    balances[address(0)] = totalSupply;

    if (totalSupply > 0) {
      Minted(address(0), totalSupply);
    }
  }

  /**
   * When token is released to be transferable, enforce no new tokens can be created.
   */
  function releaseTokenTransfer() public onlyReleaseAgent {
    super.releaseTokenTransfer();
  }

  /**
   * Allow upgrade agent functionality kick in only if the crowdsale was success.
   */
  function canUpgrade() public constant returns(bool) {
    return released && super.canUpgrade();
  }

  /**
   * Owner can update token information here
   */
  function setTokenInformation(string _name, string _symbol) onlyOwner {
    name = _name;
    symbol = _symbol;

    UpdatedTokenInformation(name, symbol);
  }

  /**
   * Owner can set upgrade client
   */
  function setUpgradeClient(address _upgradeClient) onlyOwner {
    upgradeClient = UpgradeAgent(_upgradeClient);
  }

  /**
   * Only upgrade client can upgrade tokens
   */
  function upgradeTo(address _to, uint _value) onlyUpgradeClient {
    balances[address(0)] = balances[address(0)].sub(_value);
    balances[_to] = balances[_to].add(_value);
    Transfer(address(0), _to, _value);
  }
}
