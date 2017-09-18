pragma solidity ^0.4.15;

import "./GenericCrowdsale.sol";
import "./CrowdsaleToken.sol";

// This contract has the sole objective of providing a sane concrete instance of the Crowdsale contract.
contract Crowdsale is GenericCrowdsale {
  string constant private token_name = "Ribbits";
  string constant private token_symbol = "RBT";
  uint private constant token_initial_supply = 0;
  uint8 private constant token_decimals = 16;
  bool private constant token_mintable = false;

  uint private constant blocks_between_payments =  25200;
  uint private constant token_in_wei = 5 * (10 ** 14);


  function Crowdsale(address team_multisig, uint start, uint end) GenericCrowdsale(team_multisig, start, end) public {
      token = new CrowdsaleToken(token_name, token_symbol, token_initial_supply, token_decimals, team_multisig, token_mintable, blocks_between_payments, end);
  }

  function assignTokens(address receiver, uint tokenAmount) internal {
    token.transfer(receiver, tokenAmount);
  }

  //TODO: implement token amount calculation
  function calculateTokenAmount(uint weiAmount, address agent) constant internal returns (uint);

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