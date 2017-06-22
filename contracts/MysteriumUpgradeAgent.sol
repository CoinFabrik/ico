pragma solidity ^0.4.11;

import "./Ownable.sol";
import "./MysteriumToken.sol";

/**
 * Mysterium Upgrade agent interface inspired by Lunyr.
 *
 * Upgrade agent transfers tokens to a new contract.
 */
contract MysteriumUpgradeAgent is Ownable {

  uint public originalSupply;

  MysteriumToken public mysteriumToken;

  address public originalToken;

  modifier notInitialized() {
    if (address(mysteriumToken) != 0 && address(originalToken) != 0) {
      throw;
    }
    _;
  }

  modifier initialized() {
    if (address(mysteriumToken) == 0 || address(originalToken) == 0) {
      throw;
    }
    _;
  }

  modifier onlyOriginalToken() {
    if (msg.sender != originalToken) {
      throw;
    }
    _;
  }

  function MysteriumUpgradeAgent(address _mysteriumToken, uint256 _originalSupply) {
    mysteriumToken = MysteriumToken(_mysteriumToken);
    originalSupply = _originalSupply;
  }

  function initialize(address _originalToken) public onlyOwner notInitialized {
    originalToken = _originalToken;
  }

  /** Interface marker */
  function isUpgradeAgent() public constant returns (bool) {
    return true;
  }

  function upgradeFrom(address _from, uint256 _value) public onlyOriginalToken initialized {
    mysteriumToken.upgradeTo(_from, _value);
  }
}
