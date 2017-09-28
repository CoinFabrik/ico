pragma solidity ^0.4.15;

/**
 * Authored by https://www.coinfabrik.com/
 */

import "./ERC20.sol";

contract RefundToken {
  function getRefundMaster() internal constant returns (address);

  function enableRefund(address agent, uint tokens, ERC20 token_contract) {
    require(msg.sender == getRefundMaster());
    token_contract.approve(agent, tokens);
  }
}