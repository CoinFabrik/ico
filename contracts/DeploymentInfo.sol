pragma solidity ^0.4.24;

// Simple deployment information store inside contract storage.
contract DeploymentInfo {
  uint private deployed_on;

  constructor() public {
    deployed_on = block.number;
  }


  function getDeploymentBlock() public view returns (uint) {
    return deployed_on;
  }
}
