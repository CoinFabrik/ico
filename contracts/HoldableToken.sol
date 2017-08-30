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
  mapping (address => mapping (address => uint)) allowed;

  //TODO: add configuration parameters like crowdsale
  function HoldableToken(Crowdsale _crowdsale) internal {
    heldTokensPerPayday.push(0);
    crowdsale = _crowdsale;
  }


  /**
  * @dev transfer token for a specified address
  * @param destination The address to transfer to.
  * @param value The amount to be transferred.
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

  function internalTransfer(address source, address destination, uint value) internal returns (bool success){
    uint balance = balanceOf(source);
    require(balance >= value);

    if (source == crowdsale && (endBlock == 0 || block.number <= endBlock)) {
      contributors[crowdsale].secondaryTokensBalance = contributors[crowdsale].secondaryTokensBalance.sub(value);
      contributors[destination].primaryTokensBalance = contributors[destination].primaryTokensBalance.add(value);
      heldTokensPerPayday[0] = heldTokensPerPayday[0].add(value);
    } else {
      secondaryBalance = contributors[source].secondaryTokensBalance.add(pendingRevenue(source));
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
  function allowance(address _owner, address _spender) public constant returns (uint remaining) {
    return allowed[_owner][_spender];
  }

  /**
   * @dev Aprove the passed address to spend the specified amount of tokens on behalf of msg.sender.
   * @param _spender The address which will spend the funds.
   * @param _value The amount of tokens to be spent.
   */

  function approve(address _spender, uint _value) public returns (bool success) {

    // To change the approve amount you first have to reduce the addresses'
    //  allowance to zero by calling `approve(_spender, 0)` if it is not
    //  already 0 to mitigate the race condition described here:
    //  https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729

    require (_value == 0 || allowed[msg.sender][_spender] == 0);

    allowed[msg.sender][_spender] = _value;
    Approval(msg.sender, _spender, _value);
    return true;
  }


  /**
  * Atomic increment of approved spending
  *
  * Works around https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
  *
  */
  function addApproval(address _spender, uint _addedValue) public returns (bool success) {
    uint oldValue = allowed[msg.sender][_spender];
    allowed[msg.sender][_spender] = oldValue.add(_addedValue);
    Approval(msg.sender, _spender, allowed[msg.sender][_spender]);
    return true;
  }

  /**
   * Atomic decrement of approved spending.
   *
   * Works around https://github.com/ethereum/EIPs/issues/20#issuecomment-263524729
   */
  function subApproval(address _spender, uint _subtractedValue) public returns (bool success) {
    uint oldVal = allowed[msg.sender][_spender];

    if (_subtractedValue > oldVal) {
    allowed[msg.sender][_spender] = 0;
    } else {
    allowed[msg.sender][_spender] = oldVal.sub(_subtractedValue);
    }
    Approval(msg.sender, _spender, allowed[msg.sender][_spender]);
    return true;
  }

  /**
   * @dev Transfer tokens from one address to another
   * @param _from address The address which you want to send tokens from
   * @param _to address The address which you want to transfer to
   * @param _value uint the amout of tokens to be transfered
   */
  function transferFrom(address _from, address _to, uint _value) public returns (bool success) {
    uint _allowance = allowed[_from][msg.sender];

    // Check is not needed because sub(_allowance, _value) will already throw if this condition is not met
    // require(_value <= _allowance);
    // SafeMath uses assert instead of require though, beware when using an analysis tool

    allowed[_from][msg.sender] = _allowance.sub(_value);

    result = internalTransfer(_from, _to, _value);

    Transfer(_from, _to, _value);
    return result;
  }

}