pragma solidity ^0.4.11;

import "./Ownable.sol";
import "./MysteriumToken.sol";

/**
 * Mysterium Upgrade agent interface inspired by Lunyr.
 *
 * Upgrade agent transfers tokens to a new contract.
 * Upgrade agent itself can be the token contract, or just a middle man contract doing the heavy lifting.
 */
contract MysteriumUpgradeAgent is Ownable {

  uint public originalSupply;
  MysteriumToken mysteriumToken;

  modifier notInitialized() {
    if (address(mysteriumToken) != 0) {
      throw;
    }
    _;
  }

  modifier initialized() {
    if (address(mysteriumToken) == 0) {
      throw;
    }
    _;
  }

  function MysteriumUpgradeAgent() {
  }

  function initialize(address _token) public onlyOwner notInitialized {
    MysteriumToken mysteriumToken = MysteriumToken(_token);
    originalSupply = mysteriumToken.totalSupply();
  }

  /** Interface marker */
  function isUpgradeAgent() public constant returns (bool) {
    return true;
  }

  function upgradeFrom(address _from, uint256 _value) public initialized {
    mysteriumToken.upgradeFrom(_from, _value);
  }

}
