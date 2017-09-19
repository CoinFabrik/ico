pragma solidity ^0.4.15;

/**
 * Originally from https://github.com/TokenMarketNet/ico
 * Modified by https://www.coinfabrik.com/
 */

import './FractionalERC20.sol';
import './ReleasableToken.sol';
import './UpgradeableToken.sol';

/**
 * A crowdsale token.
 *
 * An ERC-20 token designed specifically for crowdsales with investor protection and further development path.
 *
 * - The token transfer() is disabled until the crowdsale is over
 * - The token contract gives an opt-in upgrade path to a new contract
 * - The same token can be part of several crowdsales through the approve() mechanism
 * - The token can be capped (supply set in the constructor) or uncapped (crowdsale contract can mint new tokens)
 *
 */
contract CrowdsaleToken is ReleasableToken, UpgradeableToken, FractionalERC20 {

  /**
   * Construct the token.
   *
   * This token must be created through a team multisig wallet, so that it is owned by that wallet.
   *
   * @param token_name Token name string
   * @param token_symbol Token symbol - typically it's all caps
   * @param initial_supply How many tokens we start with
   * @param token_decimals Number of decimal places
   * @param team_multisig Team's multisig
   * @param blocks_between_payments Amount of blocks between each revenue payment
   * @param _end End of the crowdsale
   * @param _crowdsale Crowdsale's address
   */


  function CrowdsaleToken(string token_name, string token_symbol, uint initial_supply, uint8 token_decimals, address team_multisig, uint blocks_between_payments, uint _end, address _crowdsale)
    UpgradeableToken(team_multisig) HoldableToken(blocks_between_payments, _end, _crowdsale) {
    uint revenueTokens = initial_supply.mul(3).div(10);
    uint nonrevenueTokens = initial_supply.sub(revenue);
    contributors[crowdsale].secondaryBalance = nonrevenueTokens;
    contributors[address(this)].secondaryBalance = revenueTokens;


    name = token_name;
    symbol = token_symbol;
    decimals = token_decimals;
  }

  /**
   * When token is released to be transferable, prohibit new token creation.
   */
  function releaseTokenTransfer() public onlyReleaseAgent {
    crowdsaleExcess = contributors[crowdsale].secondaryBalance;
    internalTransfer(crowdsale, address(this), crowdsaleExcess);
    purchasable = false;
    super.releaseTokenTransfer();
  }

  /**
   * Allow upgrade agent functionality to kick in only if the crowdsale was a success.
   * TODO: Are there any other conditions when giving out dividends? Perhaps we should stop all movements.
   */
  function canUpgrade() public constant returns(bool) {
    return released && super.canUpgrade();
  }

  /**
   * Owner can update token information here
   */
  function setTokenInformation(string token_name, string token_symbol) onlyOwner {
    name = token_name;
    symbol = token_symbol;

    UpdatedTokenInformation(name, symbol);
  }
}