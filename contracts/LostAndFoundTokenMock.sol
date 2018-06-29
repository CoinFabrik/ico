pragma solidity ^0.4.24;

import "./LostAndFoundToken.sol";

// Mock class for LostAndFoundToken contract.
contract LostAndFoundTokenMock is LostAndFoundToken {

  address public master;

  constructor() public {
    master = msg.sender;
  }

	function getLostAndFoundMaster() internal view returns (address) {
    return master;
	}
}