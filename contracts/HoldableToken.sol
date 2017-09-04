pragma solidity ^0.4.13;

import './ERC20.sol';
import './SafeMath.sol';
import './Crowdsale.sol';
import './RevenueStrategy.sol';

/**
 * @title Holdable Token
 * @dev Implementation of the simplified interface in ERC20Basic that provides an incentive to hold tokens for a time after the crowdsale ends. 
 */
contract HoldableToken is ERC20 {
  using SafeMath for uint;

  uint private constant payments = 14;

  uint[] heldTokensPerPayday;
  uint blocksBetweenPayments;
  uint end;
  Crowdsale crowdsale;
  RevenueStrategy revenueStrategy;

  struct Contributor {
    uint primaryBalance;
    uint secondaryBalance;
    uint nextPayday;
  }

  mapping(address => Contributor) public contributors;
  mapping(address => mapping(address => uint)) allowed;

  //TODO: add configuration parameters like crowdsale
  function HoldableToken( uint _blocksBetweenPayments, uint _end, Crowdsale _crowdsale, RevenueStrategy _revenueStrategy ) internal {
    heldTokensPerPayday.push(0);
    blocksBetweenPayments = _blocksBetweenPayments;
    end = _end;
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
    bool result = internalTransfer(msg.sender, destination, value);
    Transfer(msg.sender, destination, value);
    return result;
  }


  /**
  * @dev Gets the balance of the specified address.
  * @param account The address to query the the balance of. 
  * @return An uint representing the amount owned by the passed address.
  */
  function balanceOf(address account) public constant returns(uint) {
    uint revenue = pendingRevenue(account);
    uint balance = revenue.add(contributors[account].secondaryBalance).add(contributors[account].primaryBalance);
    return balance;
  }
  /**
  * @dev Updates the amount of primary tokens held until each payday
  * @param curPayday The current payday
  */
  function updatePaydayAmounts(uint curPayday) private {
    if (heldTokensPerPayday.length > curPayday)
      return;
    uint heldTokens = heldTokensPerPayday[heldTokensPerPayday.length.sub(1)];
    for (uint i = heldTokensPerPayday.length; i <= curPayday; i++) {
      heldTokensPerPayday.push(heldTokens);
    }
  }

  function revenuePerPayday() internal returns (uint);

  function amountOnSale() internal returns (uint);

  function pendingRevenue(address account) internal constant returns(uint) {
    uint curPayday = currentPayday();
    uint revenue = 0;
    uint heldTokens = 0;

    for (uint i = contributors[account].nextPayday; i <= curPayday; i++) {
      uint index = i-1;
      heldTokens = index < heldTokensPerPayday.length ? heldTokensPerPayday[index] : heldTokens;
      // TODO: add interface for revenuePerPayday so it is calculated by derived contract.
      // Warning: overflow in the multiplication will block all operations for the account
      // The multiplicationagnitude of the revenue per payday should be chosen to guarantee the safety of all operations.
      // E.g. if the revenue is taken out of an initial pool of 10^23 units, all operations are safe since
      // 10^23 * 10^23 = 10^46 < 10^77 ~= 2^256
      uint pay = contributors[account].primaryBalance.mul(revenueStrategy.revenuePerPayday()).div(heldTokens);
      revenue = pay.add(revenue);
    }
    return revenue;
  }

  function currentPayday() internal constant returns (uint) {
    if (block.number <= end || end == 0) return 0;
    uint curPayday = block.number.sub(end).div(blocksBetweenPayments);
    curPayday = curPayday > payments ? payments : curPayday;
    return curPayday;
  }

  function internalTransfer(address source, address destination, uint value) private returns (bool success){
    uint balance = balanceOf(source);
    require(balance >= value);

    if (source == address(crowdsale) && (end == 0 || block.number <= end)) {
      contributors[crowdsale].secondaryBalance = contributors[crowdsale].secondaryBalance.sub(value);
      contributors[destination].primaryBalance = contributors[destination].primaryBalance.add(value);
      heldTokensPerPayday[0] = heldTokensPerPayday[0].add(value);
    } else if (source == address(this)) {
      contributors[address(this)].secondaryBalance = contributors[address(this)].secondaryBalance.sub(value);
      contributors[destination].secondaryBalance = contributors[destination].secondaryBalance.add(value);
    } else {
      uint revenue = pendingRevenue(source);
      internalTransfer(address(this), source, revenue);
      uint secondaryBalance = contributors[source].secondaryBalance;

      if (secondaryBalance < value) {
        uint spentInitialTokens = value.sub(secondaryBalance);
        contributors[source].secondaryBalance = 0;
        contributors[source].primaryBalance = contributors[source].primaryBalance.sub(spentInitialTokens);
        uint curPayday = currentPayday();

        updatePaydayAmounts(curPayday);

        heldTokensPerPayday[curPayday] = heldTokensPerPayday[curPayday].sub(spentInitialTokens);
      } else {
        contributors[source].secondaryBalance = secondaryBalance.sub(value);
        contributors[destination].secondaryBalance = contributors[destination].secondaryBalance.add(value);
      }

      contributors[source].nextPayday = curPayday.add(1);
    }
    return true;
  }

  /**
   * @dev Function to check the amount of tokens than an owner allowed to a spender.
   * @param owner address The address which owns the funds.
   * @param spender address The address which will spend the funds.
   * @return A uint specifing the amount of tokens still avaible for the spender.
   */
  function allowance(address owner, address spender) public constant returns (uint remaining) {
    return allowed[owner][spender];
  }

  /**
   * @dev Aprove the passed address to spend the specified amount of tokens on behalf of msg.sender.
   * @param spender The address which will spend the funds.
   * @param value The amount of tokens to be spent.
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
   * @param from address The address which you want to send tokens from
   * @param to address The address which you want to transfer to
   * @param value uint the amout of tokens to be transfered
   */
  function transferFrom(address from, address to, uint value) public returns (bool success) {
    uint allowance = allowed[from][msg.sender];

    // Check is not needed because sub(allowance, value) will already throw if this condition is not met
    // require(value <= allowance);
    // SafeMath uses assert instead of require though, beware when using an analysis tool

    allowed[from][msg.sender] = allowance.sub(value);

    bool result = internalTransfer(from, to, value);

    Transfer(from, to, value);
    return result;
  }

}