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

  string public name;
  string public symbol;
  uint public loyalty_program_balance;

  /**
   * Construct the token.
   *
   * This token must be created through a team multisig wallet, so that it is owned by that wallet.
   *
   * @param token_name Token name string
   * @param token_symbol Token symbol - typically it's all caps
   * @param initial_supply How many tokens we start with (including the decimal places in its representation)
   * @param token_decimals Number of decimal places
   * @param team_multisig The multisig of the team
   * @param crowdsale_end End of the crowdsale
   */
  function CrowdsaleToken(string token_name, string token_symbol, uint initial_supply, uint8 token_decimals, address team_multisig, uint crowdsale_end)
    UpgradeableToken(team_multisig) HoldableToken(crowdsale_end) {

    uint revenueTokens = initial_supply.mul(3).div(10);
    uint nonrevenueTokens = initial_supply.sub(revenueTokens);
    contributors[crowdsale].secondaryBalance = nonrevenueTokens;
    contributors[address(this)].secondaryBalance = revenueTokens;

    name = token_name;
    symbol = token_symbol;
    decimals = token_decimals;
  }

  /**
   * @dev Release token transfers which lets us establish the balance of the loyalty program.
   */
  function releaseTokenTransfer() public onlyReleaseAgent {
    uint crowdsaleExcess = balanceOf(crowdsale);
    loyalty_program_balance = balanceOf(address(this)).add(crowdsaleExcess);
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
   * @dev Internal behaviour configuration for the loyalty program.
   * @return Revenue paid to all loyal holders in a single payday.
   */
  function revenuePerPayday() constant internal returns (uint) {
    return loyalty_program_balance.div(payments);   
  }

}