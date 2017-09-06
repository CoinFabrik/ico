pragma solidity ^0.4.13;

import './ERC20.sol';
import './HoldableToken.sol';
import './SafeMath.sol';

/**
 * @title Standard Token
 * @dev This token contract extends the HoldableToken contract so it implements the ERC20 allowance mechanisms.
 */
contract StandardHoldableToken is ERC20, HoldableToken {
  using SafeMath for uint;

  mapping(address => mapping(address => uint)) public allowed;

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
    // Check out addApproval and subApproval which are the preferred workarounds though.

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