pragma solidity ^0.4.15;

import "./GenericCrowdsale.sol";
import "./CrowdsaleToken.sol";
import "./TokenTranchePricing.sol";

// This contract has the sole objective of providing a sane concrete instance of the Crowdsale contract.
contract Crowdsale is GenericCrowdsale, TokenTranchePricing {
  string constant private token_name = "Ribbits";
  string constant private token_symbol = "RBT";
  uint private constant token_initial_supply = 0;
  uint8 private constant token_decimals = 16;
  uint tokensCap = 1000000000 * (10 ** uint(token_decimals)); // One billion tokens 

  uint private constant blocks_between_payments =  25200;
  uint private constant token_in_wei = 5 * (10 ** 14);
  uint tokensAmount1HalfBillion = 500000000 * (10 ** uint(token_decimals));
  uint tokensPerWei1 = 2000 * (10 ** uint(token_decimals));
  uint[] tranches = [tokensAmount1HalfBillion, tokensPerWei1];


  function Crowdsale(address team_multisig, uint start, uint end) GenericCrowdsale(team_multisig, start, end) TokenTranchePricing(tranches) public {
    CrowdsaleToken token = new CrowdsaleToken(token_name, token_symbol, token_initial_supply, token_decimals, team_multisig, blocks_between_payments, end);
    token.setReleaseAgent(address(this));
  }

  function assignTokens(address receiver, uint tokenAmount) internal {
    token.transfer(receiver, tokenAmount);
  }

  function calculateTokenAmount(uint weiAmount, address customer) internal constant returns (uint tokenAmount){
    uint tokensPerWei = calculatePrice(tokensSold);
    tokenAmount = tokensPerWei.mul(weiAmount).mul(tokensPerWei);
  }

  function weiAllowedToReceive(uint weiAmount, address customer) internal constant returns (uint weiAllowed) {
    uint tokensPerWei = calculatePrice(tokensSold);
    weiAllowed = tokensCap.sub(tokensSold).div(tokensPerWei);
  }

  function preallocate(address receiver, uint fullTokens, uint weiPrice) public onlyOwner notFinished {
    if (weiPrice > 0) {
      super.preallocate(receiver, fullTokens, weiPrice);
    } else {
      require(receiver != address(0));
      uint tokenAmount = fullTokens.mul(10**uint(token.decimals()));
      require(tokenAmount != 0);
      tokenAmountOf[receiver] = tokenAmountOf[receiver].add(tokenAmount);
      assignTokens(receiver, tokenAmount);
    }
  }

  function finalize() public inState(State.Success) onlyOwner stopInEmergency {
    token.releaseTransfer();
    uint remaining_tokens = token.balanceOf(address(this));
    token.transfer(address(token), remaining_tokens);
  }

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