pragma solidity ^0.4.13;

/**
 * Originally from https://github.com/OpenZeppelin/zeppelin-solidity
 * Modified by https://www.coinfabrik.com/
 */

import './ERC20Basic.sol';
import './SafeMath.sol';

/**
 * @title Basic token
 * @dev Basic version of StandardToken, with no allowances. 
 */
contract HoldableToken is ERC20Basic, FractionalERC20, ReleasableToken, MintableToken {
  using SafeMath for uint;


  uint256 revenuePerWeek;

  uint256 blocksBetweenPayments;

  uint256 endBlock;

  uint256 lastCheckedWeek;

  uint256[14] heldTokensPerWeek;

  Crowdsale crowdsale

  struct Contributor {
    uint256 primaryTokensBalance;
    uint256 secondaryTokensBalance;
    uint256 nextPaymentWeek;
  }

  mapping(address => Contributor) public contributors;


  /**
  * @dev transfer token for a specified address
  * @param _to The address to transfer to.
  * @param _value The amount to be transferred.
  */
  function transfer(address _to, uint _value) public returns (bool success) { //Mergear con el released REQUERIR TODO LO NECESARIO

    balance = balanceOf(msg.sender);    
    require(balance >= _value);

    if(msg.sender == crowdsale) {
      contributors[crowdsale].secondaryTokensBalance = contributors[crowdsale].secondaryTokensBalance.sub(_value);
      contributors[_to].primaryTokensBalance = contributors[_to].primaryTokensBalance.add(_value);
      heldTokensPerWeek[0] = heldTokensPerWeek[0].add(_value);
    } else {
      secondaryBalance = contributors[msg.sender].secondaryTokensBalance.add(pendingRevenue(msg.sender));
      if(secondaryBalance < _value) {
        spentInitialTokens = _value.sub(secondaryBalance);
        contributors[msg.sender].secondaryTokensBalance = 0;
        contributors[msg.sender].primaryTokensBalance = contributors[msg.sender].primaryTokensBalance.sub(spentInitialTokens);
        actualPaymentWeek = currentPaymentWeek();
        lastHeldAmount = 0;
        for (i = 0; i < actualPaymentWeek; i++) {
          lastHeldAmount = heldTokensPerWeek[i] > 0 ? heldTokensPerWeek : lastHeldAmount;
          if(heldTokensPerWeek[i] == 0) {
            heldTokensPerWeek[i] = lastHeldAmount;
          }
        }
        heldTokensPerWeek[actualPaymentWeek] = heldTokensPerWeek[actualPaymentWeek].sub(spentInitialTokens);
      } else {
        contributors[msg.sender].secondaryTokensBalance = secondaryBalance.sub(_value);
        contributors[_to].secondaryTokensBalance = contributors[_to].secondaryTokensBalance.add(_value);
      }

      contributors[_owner].nextPaymentWeek = currentPaymentWeek.add(1);      
    }
    Transfer(msg.sender, _to, _value);
    return true;
  }

  /**
  * @dev Gets the balance of the specified address.
  * @param _owner The address to query the the balance of. 
  * @return An uint representing the amount owned by the passed address.
  */
  function balanceOf(address _owner) public constant returns(uint) {
    if(!released) { //OR OTHER FLAG
      return contributors[_owner].primaryTokensBalance;
    } else {
      revenue = pendingRevenue(_owner);
      balance = revenue.add(contributors[_owner].secondaryTokensBalance).add(contributors[_owner].primaryTokensBalance);
      return balance;
    }
  }

  function pendingRevenue(address _owner) internal constant returns(uint) {
    actualPaymentWeek = currentPaymentWeek();
    revenue = 0;

    for (i = contributors[_owner].nextPaymentWeek; i <= actualPaymentWeek; i++) {
      lastHeldAmount = heldTokensPerWeek[i] > 0 ? heldTokensPerWeek : lastHeldAmount; 
      tokensPerHeld = revenuePerWeek.div(lastHeldAmount);
      revenue = contributors[_owner].primaryTokensBalance.mul(tokensPerHeld).add(revenue);
    }
    return revenue;
  }

  function currentPaymentWeek() internal constant returns (uint) {
    actualPaymentWeek = block.number.sub(endBlock).div(blocksBetweenPayments);
    actualPaymentWeek = actualPaymentWeek > 14 ? 14 : actualPaymentWeek;
    return actualPaymentWeek;
  } 

}