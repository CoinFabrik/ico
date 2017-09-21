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
  uint decimalTokensCap = 1000000000 * (10 ** uint(token_decimals)); // One billion tokens 

  uint private constant blocks_between_payments =  25200;
  uint private constant token_in_wei = 5 * (10 ** 14);
  uint decimalTokensAmount1HalfBillion = 500000000 * (10 ** uint(token_decimals));
  uint decimalTokensPerWei1 = 2000 * (10 ** uint(token_decimals));
  uint[] _tranches = [decimalTokensAmount1HalfBillion, decimalTokensPerWei1];


  function Crowdsale(address team_multisig, uint start, uint end) GenericCrowdsale(team_multisig, start, end) TokenTranchePricing(_tranches) public {
    CrowdsaleToken token = new CrowdsaleToken(token_name, token_symbol, token_initial_supply, token_decimals, team_multisig, blocks_between_payments, end);
  }

  function assignTokens(address receiver, uint tokenAmount) internal {
    token.transfer(receiver, tokenAmount);
  }

  function calculateTokenAmount(uint weiAmount, address customer) internal constant returns (uint tokenAmount){
    uint decimalTokensPerWei = calculatePrice(tokensSold);
    tokenAmount = decimalTokensPerWei.mul(weiAmount).mul(decimalTokensPerWei);
  }

  function weiAllowedToReceive(uint weiAmount, address customer) internal constant returns (uint weiAllowed) {
    uint decimalTokensPerWei = calculatePrice(tokensSold);
    weiAllowed = decimalTokensCap.sub(tokensSold).div(decimalTokensPerWei);
  }

  function preallocate(address receiver, uint fullTokens, uint weiPrice) public onlyOwner notFinished {
    require(receiver != address(0));
    uint tokenAmount = fullTokens.mul(10**uint(token.decimals()));
    require(tokenAmount != 0);
    uint weiAmount = weiPrice.mul(tokenAmount); // This can also be 0, in which case we give out tokens for free
    if(weiAmount > 0) {
      super.preallocate(receiver, fullTokens, weiPrice);
    } else {
      tokenAmountOf[receiver] = tokenAmountOf[receiver].add(tokenAmount);
      assignTokens(receiver, tokenAmount);
    }
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