pragma solidity ^0.4.23;

import "../MintableToken.sol";

// Mock class for MintableToken contract.
contract MintableTokenMock is MintableToken {
  
  uint private total_supply;
  mapping(address => uint) public balances;

  constructor(uint initialSupply, address multisig, bool mintable) MintableToken(initialSupply, multisig, mintable) public {}

  function mintInternal(address receiver, uint amount) internal {
    total_supply = total_supply.add(amount);
    balances[receiver] = balances[receiver].add(amount);
  }

  function totalSupply() public view returns (uint) { return total_supply; }
  function balanceOf(address customer) public view returns (uint) { return balances[customer]; }
  function transfer(address, uint) public returns (bool) { revert(); }
}