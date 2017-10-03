pragma solidity ^0.4.15;

/**
 * Originally from https://github.com/TokenMarketNet/ico
 * Modified by https://www.coinfabrik.com/
 */

import "./FractionalERC20.sol";
import "./ReleasableToken.sol";
import "./UpgradeableToken.sol";
import "./LostAndFoundToken.sol";

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
contract CrowdsaleToken is ReleasableToken, UpgradeableToken, FractionalERC20, LostAndFoundToken {

  string public name = "Ribbits";
  string public symbol = "RBT";
  uint public loyalty_program_supply;

  address public lost_and_found_master;

  /**
   * Construct the token.
   *
   * This token must be created through a team multisig wallet, so that it is owned by that wallet.
   *
   * @param initial_supply How many tokens we start with (including the decimal places in its representation)
   * @param token_decimals Number of decimal places
   * @param team_multisig The multisig of the team
   * @param crowdsale_end End of the crowdsale
   * @param token_retriever Address of the account that handles ERC20 tokens that were accidentally sent to this contract.
   */
  function CrowdsaleToken(uint initial_supply, uint8 token_decimals, address team_multisig, uint crowdsale_end, address token_retriever) public
  UpgradeableToken(team_multisig) HoldableToken(crowdsale_end) {

    require(token_retriever != address(0));
    uint revenueTokens = initial_supply.mul(3).div(10);
    uint nonrevenueTokens = initial_supply.sub(revenueTokens);
    contributors[crowdsale].secondaryBalance = nonrevenueTokens;
    contributors[address(this)].secondaryBalance = revenueTokens;

    decimals = token_decimals;
    lost_and_found_master = token_retriever;
  }

  /**
   * @dev Release token transfers which lets us establish the balance of the loyalty program.
   */
  function releaseTokenTransfer() public onlyReleaseAgent {
    uint crowdsaleExcess = balanceOf(crowdsale);
    loyalty_program_supply = balanceOf(address(this)).add(crowdsaleExcess);
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
    return loyalty_program_supply.div(payments);
  }

  // Safe override of the token recover mechanism for this implementation
  function enableLostAndFound(address agent, uint tokens, ERC20 token_contract) {
    require(released);
    // Safeguard for the tokens of the loyalty program
    require(balanceOf(address(this)).add(loyalty_program_paid).sub(loyalty_program_supply) >= tokens);
    super.enableLostAndFound(agent, tokens, token_contract);
  }

  function getLostAndFoundMaster() internal constant returns(address) {
    return lost_and_found_master;
  }

}