pragma solidity ^0.4.19;

/**
 * Originally from https://github.com/TokenMarketNet/ico
 * Modified by https://www.coinfabrik.com/
 */

import "./ReleasableToken.sol";
import "./UpgradeableToken.sol";
import "./LostAndFoundToken.sol";
import "./MintableToken.sol";

/**
 * A crowdsale token.
 *
 * An ERC-20 token designed specifically for crowdsales with investor protection and further development path.
 *
 * - The token transfer() is disabled until the crowdsale is over
 * - The token contract gives an opt-in upgrade path to a new contract
 * - The same token can be part of several crowdsales through the approve() mechanism
 * - The token can be capped (supply set in the constructor) or uncapped (crowdsale contract can mint new tokens)
 * - ERC20 tokens transferred to this contract can be recovered by a lost and found master
 *
 */
contract CrowdsaleToken is ReleasableToken, MintableToken, UpgradeableToken, LostAndFoundToken {

  string public name = "Cryptosolartech";

  string public symbol = "CST";

  uint8 public decimals;

  address public lost_and_found_master;

  /**
   * Construct the token.
   *
   * This token must be created through a team multisig wallet, so that it is owned by that wallet.
   *
   * @param initial_supply How many tokens we start with.
   * @param token_decimals Number of decimal places.
   * @param team_multisig Address of the multisig that receives the initial supply and is set as the upgrade master.
   * @param token_retriever Address of the account that handles ERC20 tokens that were accidentally sent to this contract.
   */
  function CrowdsaleToken(uint initial_supply, uint8 token_decimals, address team_multisig, address token_retriever) public
  UpgradeableToken(team_multisig) MintableToken(initial_supply, team_multisig, true) {
    require(token_retriever != address(0));
    decimals = token_decimals;
    lost_and_found_master = token_retriever;
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
  function canUpgrade() public view returns(bool) {
    return released && super.canUpgrade();
  }

  function burn(uint value) public {
    burnTokens(msg.sender, value);
  }

  function getLostAndFoundMaster() internal view returns(address) {
    return lost_and_found_master;
  }
}