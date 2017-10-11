pragma solidity ^0.4.15;

import "../MintableToken.sol";

// Mock class for MintableToken contract.
contract MintableTokenMock is MintableToken {
  
  mapping(address => uint) balances;

  function MintableTokenMock(uint initialSupply, address multisig, bool mintable) MintableToken(initialSupply, multisig, mintable) public {}

  function mintInternal(address receiver, uint amount) internal {
    totalSupply = totalSupply.add(amount);
    balances[receiver] = balances[receiver].add(amount);
  }

  function balanceOf(address customer) public constant returns (uint){return balances[customer];}
  function transfer(address to, uint value) public returns (bool ok){revert();}
}