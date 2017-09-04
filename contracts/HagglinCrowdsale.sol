pragma solidity ^0.4.13;

import './Crowdsale.sol';
import './HagglinToken.sol';
import './FlatPricing.sol';
import './FixedCeiling.sol';
import './StandardFinalizeAgent.sol';
import './RevenueStrategy.sol';

// This contract has the sole objective of providing a sane concrete instance of the Crowdsale contract.
contract HagglinCrowdsale is Crowdsale {
  uint private constant chunked_multiple = 18000 * (10 ** 18); // in wei
  uint private constant limit_per_address = 100000 * (10 ** 18); // in wei
  uint private constant hagglin_minimum_funding = 17000 * (10 ** 18); // in wei
  uint private constant token_in_wei = 5 * (10 ** 14);
  uint private constant token_initial_supply = (10 ** 9) * token_in_wei;
  uint8 private constant token_decimals = 14;
  function HagglinCrowdsale(address _teamMultisig, uint _start, uint _end) Crowdsale(_teamMultisig, _start, _end, hagglin_minimum_funding) public {
    PricingStrategy p_strategy = new FlatPricing(token_in_wei);
    CeilingStrategy c_strategy = new FixedCeiling(chunked_multiple, limit_per_address);
    RevenueStrategy r_strategy = new RevenueStrategy();
    // Set to dummy finalize agent that only releases the token transfer.
    FinalizeAgent f_agent = new StandardFinalizeAgent(this);
    setPricingStrategy(p_strategy);
    setCeilingStrategy(c_strategy);
    // Testing values
    token = new HagglinToken(token_initial_supply, token_decimals, _teamMultisig, _end, this, r_strategy);
    token.setReleaseAgent(address(f_agent));
    setFinalizeAgent(f_agent);
  }
    
  function assignTokens(address receiver, uint tokenAmount) internal {
    token.transfer(receiver, tokenAmount);
  }

  // These two setters are present only to correct block numbers if they are off from their target date by more than, say, a day
  function setStartingBlock(uint startingBlock) public onlyOwner inState(State.PreFunding) {
      require(startingBlock > block.number && startingBlock < endsAt);
      startsAt = startingBlock;
  }

  function setEndingBlock(uint endingBlock) public onlyOwner notFinished {
      require(endingBlock > block.number && endingBlock > startsAt);
      endsAt = endingBlock;
  }
}