pragma solidity ^0.4.21;

import "./LostAndFoundToken.sol";

// Mock class for LostAndFoundToken contract.
contract LostAndFoundTokenMock is LostAndFoundToken {

  address public master;

  function LostAndFoundTokenMock() public {
    master = msg.sender;
  }

	function getLostAndFoundMaster() internal view returns (address) {
    return master;
	}
}