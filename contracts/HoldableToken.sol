pragma solidity ^0.4.13;

/**
 * Originally from https://github.com/Op  enZeppelin/zeppelin-solidity
 * Modified by https://www.coinfabrik.com/
 */

import './ERC20Basic.sol';
import './SafeMath.sol';

/**
 * @title Holdable Token
 * @dev Implementation of the simplified interface in ERC20Basic that provides an incentive to hold tokens for a time after the crowdsale ends. 
 */
contract HoldableToken is ERC20 {
  using SafeMath for uint;

  uint private constant payments = 14;

  uint[] heldTokensPerPayday;
  uint blocksBetweenPayments;
  uint endBlock;
  Crowdsale crowdsale;
  RevenueStrategy revenueStrategy;

  struct Contributor {
    uint primaryTokensBalance;
    uint secondaryTokensBalance;
    uint nextPayday;
  }

  mapping(address => Contributor) public contributors;
  mapping (address => mapping (address => uint)) allowed;

  //TODO: add configuration parameters like crowdsale
  function HoldableToken( uint _blocksBetweenPayments, uint, _endBlock, Crowdsale _crowdsale, RevenueStrategy _revenueStrategy ) internal {
    heldTokensPerPayday.push(0);
    blocksBetweenPayments = _blocksBetweenPayments;
    endBlock = _endBlock;
    crowdsale = _crowdsale;
    revenueStrategy = _revenueStrategy;

    internalTransfer(address(this), crowdsale, amountOnSale());
  }


  /**
  * @dev transfer token for a specified address
  * @param destination The address to transfer to.
  * @param value The amount to be transferred.
  * @return true on  success
  */
  function transfer(address destination, uint value) public returns (bool success) {
    result = internalTransfer(msg.sender);
    Transfer(_from, _to, _value);
    return result;
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
  /**
  * @dev Updates the amount of primary tokens held until each payday
  * @param the current payday
  */
  function updatePaydayAmounts(uint curPayday) private {
    if (heldTokensPerPayday.length() > curPayday)
      return;
    uint heldTokens = heldTokensPerPayday[heldTokensPerPayday.length().sub(1)];
    for (uint i = heldTokensPerPayday.length(); i <= curPayday; i++) {
      heldTokensPerPayday.push(heldTokens);
    }
  }

  function revenuePerPayday() internal return (uint);

  function amountOnSale() internal return (uint);

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
      uint pay = contributors[account].primaryTokensBalance.mul(revenueStrategy.revenuePerPayday()).div(heldTokens);
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

  function internalTransfer(address source, address destination, uint value) internal returns (bool success){
    uint balance = balanceOf(source);
    require(balance >= value);

    if (source == crowdsale && (endBlock == 0 || block.number <= endBlock)) {
      contributors[crowdsale].secondaryTokensBalance = contributors[crowdsale].secondaryTokensBalance.sub(value);
      contributors[destination].primaryTokensBalance = contributors[destination].primaryTokensBalance.add(value);
      heldTokensPerPayday[0] = heldTokensPerPayday[0].add(value);
    } else if (source == address(this)) {
      contributors[address(this)].secondaryBalance = contributors[address(this)].secondaryBalance.sub(value);
      contributors[destination].secondaryBalance = contributors[destination].secondaryBalance.add(value);
    } else {
      revenue = pendingRevenue(source);
      internalTransfer(address(this), source, revenue);
      secondaryBalance = contributors[source].secondaryTokensBalance;

      if (secondaryBalance < value) {
        spentInitialTokens = value.sub(secondaryBalance);
        contributors[source].secondaryTokensBalance = 0;
        contributors[source].primaryTokensBalance = contributors[source].primaryTokensBalance.sub(spentInitialTokens);
        uint curPayday = currentPayday();

        updatePaydayAmounts(curPayday);

        heldTokensPerPayday[curPayday] = heldTokensPerPayday[curPayday].sub(spentInitialTokens);
      } else {
        contributors[source].secondaryTokensBalance = secondaryBalance.sub(value);
        contributors[destination].secondaryTokensBalance = contributors[destination].secondaryTokensBalance.add(value);
      }

      contributors[source].nextPayday = curPayday.add(1);
    }
    return true;
  }

  /**
   * @dev Function to check the amount of tokens than an owner allowed to a spender.
   * @param _owner address The address which owns the funds.
   * @param _spender address The address which will spend the funds.
   * @return A uint specifing the amount of tokens still avaible for the spender.
   */
  function allowance(address owner, address spender) public constant returns (uint remaining) {
    return allowed[owner][spender];
  }

  /**
   * @dev Aprove the passed address to spend the specified amount of tokens on behalf of msg.sender.
   * @param _spender The address which will spend the funds.
   * @param _value The amount of tokens to be spent.
   */

  function approve(address spender, uint value) public returns (bool success) {

    // To change the approve amount you first have to reduce the addresses'
    //  allowance to zero by calling `approve(spender, 0)` if it is not
    //  already 0 to mitigate the race condition described here:
    //  https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729

    require (value == 0 || allowed[msg.sender][spender] == 0);

    allowed[msg.sender][spender] = value;
    Approval(msg.sender, spender, value);
    return true;
  }


  /**
  * Atomic increment of approved spending
  *
  * Works around https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
  *
  */
  function addApproval(address spender, uint addedValue) public returns (bool success) {
    uint oldValue = allowed[msg.sender][spender];
    allowed[msg.sender][spender] = oldValue.add(addedValue);
    Approval(msg.sender, spender, allowed[msg.sender][spender]);
    return true;
  }

  /**
   * Atomic decrement of approved spending.
   *
   * Works around https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
   */
  function subApproval(address spender, uint subtractedValue) public returns (bool success) {
    uint oldVal = allowed[msg.sender][spender];

    if (subtractedValue > oldVal) {
    allowed[msg.sender][spender] = 0;
    } else {
    allowed[msg.sender][spender] = oldVal.sub(subtractedValue);
    }
    Approval(msg.sender, spender, allowed[msg.sender][spender]);
    return true;
  }

  /**
   * @dev Transfer tokens from one address to another
   * @param _from address The address which you want to send tokens from
   * @param _to address The address which you want to transfer to
   * @param _value uint the amout of tokens to be transfered
   */
  function transferFrom(address from, address to, uint value) public returns (bool success) {
    uint allowance = allowed[from][msg.sender];

    // Check is not needed because sub(allowance, value) will already throw if this condition is not met
    // require(value <= allowance);
    // SafeMath uses assert instead of require though, beware when using an analysis tool

    allowed[from][msg.sender] = allowance.sub(value);

    result = internalTransfer(from, to, value);

    Transfer(from, to, value);
    return result;
  }

}