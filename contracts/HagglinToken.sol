pragma solidity ^0.4.13;

/**
 * Originally from https://github.com/TokenMarketNet/ico
 * Modified by https://www.coinfabrik.com/
 */

import './FractionalERC20.sol';
import './ReleasableToken.sol';
import './MintableToken.sol';
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
contract HagglinToken is ReleasableToken, MintableToken, UpgradeableToken, FractionalERC20 {

  string constant public name = "Ribbits";
  string constant public symbol = "RBT";
  uint blocksBetweenPayments =  25200; //considering an average block time of 25s, the number of blocks that are created in a week.
  uint end;

  /**
   * Construct the token.
   *
   * This token must be created through a team multisig wallet, so that it is owned by that wallet.
   *
   * @param _initialSupply How many tokens we start with
   * @param _decimals Number of decimal places
   * @param _multisig Hagglin's multisig
   * @param _end End of the crowdsale
   */
  function HagglinToken(uint _initialSupply, uint8 _decimals, address _multisig, uint _end, Crowdsale _crowdsale)
    UpgradeableToken(_multisig) MintableToken(_initialSupply, msg.sender, false) HoldableToken(blocksBetweenPayments, _end, _crowdsale) {
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
   * TODO: Are there any other conditions when giving out dividends? Perhaps we should stop all movements.
   */
  function canUpgrade() public constant returns(bool) {
    return released && super.canUpgrade();
  }

}