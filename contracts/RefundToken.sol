pragma solidity ^0.4.15;

/**
 * Authored by https://www.coinfabrik.com/
 */

import "./ERC20.sol";

// This contract aims to provide an inheritable way to recover tokens from a contract not meant to hold tokens
// To use this contract, have your token-ignoring contract inherit this one and implement getRefundMaster to decide who can refund tokens.
// Of course, this contract imposes support costs upon whoever is the refund master.
contract RefundToken {
  /**
   * @return Address of the account that handles refunds.
   */
  function getRefundMaster() internal constant returns (address);

  /**
   * @param agent Address that will be able to move tokens with transferFrom
   * @param tokens Amount of tokens approved for transfer
   * @param token_contract Contract of the token
   */
  function enableRefund(address agent, uint tokens, ERC20 token_contract) public {
    require(msg.sender == getRefundMaster());
    token_contract.approve(agent, tokens);
  }
}