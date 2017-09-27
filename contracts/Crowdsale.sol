pragma solidity ^0.4.15;

import "./GenericCrowdsale.sol";
import "./CrowdsaleToken.sol";
// import "./BonusFinalizeAgent.sol";

// This contract has the sole objective of providing a sane concrete instance of the Crowdsale contract.
contract Crowdsale is GenericCrowdsale {
  uint private constant token_initial_supply = 0;
  uint8 private constant token_decimals = 15;
  bool private constant token_mintable = true;
  // The fraction of 10,000 out of the total target tokens that is used to mint bonus tokens. These are allocated to the team's multisig wallet.
  uint private constant bonus_base_points = 3000;
  uint private constant funding_cap = 10000;
  function Crowdsale(address team_multisig, uint start, uint end, address token_retriever) GenericCrowdsale(team_multisig, start, end) public {
      // FinalizeAgent f_agent = new BonusFinalizeAgent(this, bonus_base_points, team_multisig);
      // Testing values
      token = new CrowdsaleToken(token_initial_supply, token_decimals, team_multisig, token_mintable, token_retriever);
      token.setMintAgent(address(this), true);
      // token.setMintAgent(address(f_agent), true);
      // token.setReleaseAgent(address(f_agent));
      // setFinalizeAgent(f_agent);
      // Need to set a cap here or expose a public setter in the contract.
  }

  //TODO: implement token assignation (e.g. through minting or transfer)
  function assignTokens(address receiver, uint tokenAmount) internal;

  //TODO: implement token amount calculation
  function calculateTokenAmount(uint weiAmount, address agent) internal constant returns (uint weiAllowed, uint tokenAmount);

  // These two setters are present only to correct block numbers if they are off from their target date by more than, say, a day
  // Uncomment only if necessary
  // function setStartingBlock(uint startingBlock) public onlyOwner inState(State.PreFunding) {
  //     require(startingBlock > block.number && startingBlock < endsAt);
  //     startsAt = startingBlock;
  // }

  // function setEndingBlock(uint endingBlock) public onlyOwner notFinished {
  //     require(endingBlock > block.number && endingBlock > startsAt);
  //     endsAt = endingBlock;
  // }
}