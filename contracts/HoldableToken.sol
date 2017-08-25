pragma solidity ^0.4.13;

/**
 * Originally from https://github.com/OpenZeppelin/zeppelin-solidity
 * Modified by https://www.coinfabrik.com/
 */

import './ERC20Basic.sol';
import './SafeMath.sol';

/**
 * @title Holdable Token
 * @dev Implementation of the simplified interface in ERC20Basic that provides an incentive to hold tokens for a time after the crowdsale ends. 
 */
contract HoldableToken is ERC20Basic {
  using SafeMath for uint;

  uint private constant payments = 14; 

  uint blocksBetweenPayments;
  uint endBlock;
  uint[] heldTokensPerPayday;
  Crowdsale crowdsale;

  struct Contributor {
    uint primaryTokensBalance;
    uint secondaryTokensBalance;
    uint nextPayday;
  }

  mapping(address => Contributor) public contributors;

  //TODO: add configuration parameters like crowdsale
  function HoldableToken() internal {
    heldTokensPerPayday.push(0);
  }


  /**
  * @dev transfer token for a specified address
  * @param destination The address to transfer to.
  * @param value The amount to be transferred.
  */
  function transfer(address destination, uint value) public returns (bool success) {

    uint balance = balanceOf(msg.sender);
    require(balance >= value);

    if (msg.sender == crowdsale && (endBlock == 0 || block.number <= endBlock)) {
      contributors[crowdsale].secondaryTokensBalance = contributors[crowdsale].secondaryTokensBalance.sub(value);
      contributors[destination].primaryTokensBalance = contributors[destination].primaryTokensBalance.add(value);
      heldTokensPerPayday[0] = heldTokensPerPayday[0].add(value);
    } else {
      secondaryBalance = contributors[msg.sender].secondaryTokensBalance.add(pendingRevenue(msg.sender));
      if (secondaryBalance < value) {
        spentInitialTokens = value.sub(secondaryBalance);
        contributors[msg.sender].secondaryTokensBalance = 0;
        contributors[msg.sender].primaryTokensBalance = contributors[msg.sender].primaryTokensBalance.sub(spentInitialTokens);

        uint curPayday = currentPayday();
        updatePaydayAmounts(curPayday);

        heldTokensPerPayday[curPayday] = heldTokensPerPayday[curPayday].sub(spentInitialTokens);
      } else {
        contributors[msg.sender].secondaryTokensBalance = secondaryBalance.sub(value);
        contributors[destination].secondaryTokensBalance = contributors[destination].secondaryTokensBalance.add(value);
      }

      contributors[_owner].nextPayday = curPayday.add(1);
    }
    Transfer(msg.sender, destination, value);
    return true;
  }

  /**
  * @dev Gets the balance of the specified address.
  * @param account The address to query the the balance of. 
  * @return An uint representing the amount owned by the passed address.
  */
  function balanceOf(address account) public constant returns(uint) {
    uint revenue = pendingRevenue(account);
    balance = revenue.add(contributors[account].secondaryTokensBalance).add(contributors[account].primaryTokensBalance);
    return balance;
  }

  function updatePaydayAmounts(uint curPayday) private {
    if (heldTokensPerPayday.length() > curPayday)
      return;
    uint heldTokens = heldTokensPerPayday[heldTokensPerPayday.length().sub(1)];
    for (uint i = heldTokensPerPayday.length(); i <= curPayday; i++) {
      heldTokensPerPayday.push(heldTokens);
    }
  }

  function revenuePerPayday() internal return (uint);

  function pendingRevenue(address account) internal constant returns(uint) {
    uint curPayday = currentPayday();
    uint revenue = 0;
    uint heldTokens = 0;

    for (uint i = contributors[account].nextPayday; i <= curPayday; i++) {
      uint index = i-1;
      heldTokens = index < heldTokensPerPayday.length() ? heldTokensPerPayday[index] : heldTokens;
      // TODO: add interface for revenuePerPayday so it is calculated by derived contract.
      // Warning: overflow in the multiplication will block all operations for the account
      // The magnitude of the revenue per payday should be chosen to guarantee the safety of all operations.
      // E.g. if the revenue is taken out of an initial pool of 10^23 units, all operations are safe since
      // 10^23 * 10^23 = 10^46 < 10^77 ~= 2^256
      uint pay = contributors[account].primaryTokensBalance.mul(revenuePerPayday()).div(heldTokens);
      revenue = pay.add(revenue);
    }
    return revenue;
  }

  function currentPayday() internal constant returns (uint) {
    if (block.number <= endBlock || endBlock == 0) return 0;
    uint curPayday = block.number.sub(endBlock).div(blocksBetweenPayments);
    curPayday = curPayday > payments ? payments : curPayday;
    return curPayday;
  } 

}