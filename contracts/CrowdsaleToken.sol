pragma solidity ^0.4.15;

/**
 * Originally from https://github.com/TokenMarketNet/ico
 * Modified by https://www.coinfabrik.com/
 */

import "./FractionalERC20.sol";
import "./ReleasableToken.sol";
import "./MintableToken.sol";
import "./UpgradeableToken.sol";
import "./RefundToken.sol";

/**
 * A crowdsale token.
 *
 * An ERC-20 token designed specifically for crowdsales with investor protection and further development path.
 *
 * - The token transfer() is disabled until the crowdsale is over
 * - The token contract gives an opt-in upgrade path to a new contract
 * - The same token can be part of several crowdsales through the approve() mechanism
 * - The token can be capped (supply set in the constructor) or uncapped (crowdsale contract can mint new tokens)
 * - ERC20 tokens transferred to this contract can be recovered by a refunding master
 *
 */
contract CrowdsaleToken is ReleasableToken, MintableToken, UpgradeableToken, FractionalERC20, RefundToken {

  string public name = "BurgerKoenig";

  string public symbol = "BK";

  /**
   * Construct the token.
   *
   * This token must be created through a team multisig wallet, so that it is owned by that wallet.
   *
   * @param initial_supply How many tokens we start with.
   * @param token_decimals Number of decimal places.
   * @param team_multisig Address of the multisig that receives the initial supply and is set as the upgrade master.
   * @param mintable Are new tokens created over the crowdsale or do we distribute only the initial supply? Note that when the token becomes transferable the minting always ends.
   * @param token_retriever Address of the account that handles refunds of tokens that would be otherwise lost in this contract.
   */
  function CrowdsaleToken(uint initial_supply, uint8 token_decimals, address team_multisig, bool mintable, address token_retriever) public
  UpgradeableToken(team_multisig) MintableToken(initial_supply, team_multisig, mintable) RefundToken(token_retriever) {
    decimals = token_decimals;
  }

  /**
   * When token is released to be transferable, prohibit new token creation.
   */
  function releaseTokenTransfer() public onlyReleaseAgent {
    mintingFinished = true;
    super.releaseTokenTransfer();
  }

  /**
   * Allow upgrade agent functionality to kick in only if the crowdsale was a success.
   */
  function canUpgrade() public constant returns(bool) {
    return released && super.canUpgrade();
  }

}