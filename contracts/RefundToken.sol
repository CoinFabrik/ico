pragma solidity ^0.4.15;

/**
 * Authored by https://www.coinfabrik.com/
 */

import "./ERC20.sol";

contract RefundToken {
  address public refund_master;

  function RefundToken(address master) internal {
    require(master != address(0));
    refund_master = master;
  }

  function enableRefund(address agent, uint tokens, ERC20 token_contract) {
    require(msg.sender == refund_master);
    token_contract.approve(agent, tokens);
  }
}