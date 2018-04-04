pragma solidity ^0.4.19;

// Simple deployment information store inside contract storage.
contract DeploymentInfo {
  uint private deployed_on;

  function DeploymentInfo() public {
    deployed_on = block.number;
  }


  function getDeploymentBlock() public view returns (uint) {
    return deployed_on;
  }
}
