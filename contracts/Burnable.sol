pragma solidity ^0.4.15;

// Interface for burning tokens
interface Burnable {
  function burnTokens(address account, uint value) internal;
  event Burned(address account, uint value);
}