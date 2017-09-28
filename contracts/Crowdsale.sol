pragma solidity ^0.4.15;

import "./GenericCrowdsale.sol";
import "./CrowdsaleToken.sol";
import "./TokenTranchePricing.sol";

// This contract has the sole objective of providing a sane concrete instance of the Crowdsale contract.
contract Crowdsale is GenericCrowdsale, TokenTranchePricing {
  uint private constant token_initial_supply = 1000000000 * (10 ** uint(token_decimals)); // One billion tokens
  uint8 private constant token_decimals = 16;
  uint private constant tokensCap = 400000000 * (10 ** uint(token_decimals)); // 40% of a billion tokens 

  uint private constant firstTranche = 100000 * (10 ** uint(token_decimals));
  uint private constant firstTranchePrice = 2000 * (10 ** uint(token_decimals)) / 1 ether;
  uint private constant secondTranche = 400000 * (10 ** uint(token_decimals));
  uint private constant secondTranchePrice = 2000 * (10 ** uint(token_decimals)) / 1 ether;  
  uint[] private tranches_conf = [firstTranche, firstTranchePrice, secondTranche, secondTranchePrice];


  function Crowdsale(address team_multisig, uint start, uint end, address token_retriever) GenericCrowdsale(team_multisig, start, end) TokenTranchePricing(tranches_conf) public {
    CrowdsaleToken token = new CrowdsaleToken(token_initial_supply, token_decimals, team_multisig, end, token_retriever);
    token.setReleaseAgent(address(this));
    token.setTransferAgent(address(this));
  }

  /**
   * @dev We transfer tokens from this contract so they get converted into primary tokens during the transfer.
   */
  function assignTokens(address receiver, uint tokenAmount) internal {
    token.transfer(receiver, tokenAmount);
  }

  /**
   * The price is provided by the TokenTranchePricing contract
   */
  function calculateTokenAmount(uint weiAmount, address customer) internal constant returns (uint weiAllowed, uint tokenAmount){
    uint tokensPerWei = getCurrentPrice(tokensSold);
    uint maxAllowed = tokensCap.sub(tokensSold).div(tokensPerWei);
    weiAllowed = maxAllowed.min256(weiAmount);
    if (weiAmount < maxAllowed) {
      tokenAmount = tokensPerWei.mul(weiAmount);
    }
    // With this case we let the crowdsale end even when there are rounding errors due to the tokens to wei ratio
    else {
      tokenAmount = tokensCap.sub(tokensSold);
    }
  }

  /**
   * @dev We override the preallocate function so we can use it to transfer the share of the team and the charity when the price is zero.
   */
  function preallocate(address receiver, uint fullTokens, uint weiPrice) public onlyOwner notFinished {
    if (weiPrice > 0) {
      super.preallocate(receiver, fullTokens, weiPrice);
    } else {
      require(receiver != address(0));
      uint tokensOnSale = tokensCap.sub(tokensSold);
      uint availableTeamTokens = token.balanceOf(address(this)).sub(tokensOnSale);
      uint tokenAmount = fullTokens.mul(10**uint(token.decimals()));
      require(availableTeamTokens >= tokenAmount);
      require(tokenAmount != 0);
      tokenAmountOf[receiver] = tokenAmountOf[receiver].add(tokenAmount);
      assignTokens(receiver, tokenAmount);
    }
  }

  /**
   * @dev This override ensures the token is released and the remaining tokens are transferred to the loyalty program.
   */
  function finalize() public inState(State.Success) onlyOwner stopInEmergency {
    // Ordering is important: releasing the tokens avoids transferring primary tokens to the token contract
    token.releaseTokenTransfer();
    uint remaining_tokens = token.balanceOf(address(this));
    token.transfer(address(token), remaining_tokens);
  }

}