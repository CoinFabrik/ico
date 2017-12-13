pragma solidity ^0.4.18;

// Simple deployment information store inside contract storage.
contract DeploymentInfo {
  uint private deployed_on;

  function DeploymentInfo() public {
    deployed_on = block.number;
  }


  function getDeploymentBlock() public constant {
    return deployed_on;
  }
}
