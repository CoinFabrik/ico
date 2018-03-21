pragma solidity ^0.4.21;

/**
 * Authored by https://www.coinfabrik.com/
 */

import "./GenericCrowdsale.sol";
import "./CrowdsaleToken.sol";
import "./LostAndFoundToken.sol";
import "./DeploymentInfo.sol";
import "./TokenTranchePricing.sol";

// This contract has the sole objective of providing a sane concrete instance of the Crowdsale contract.
contract Crowdsale is GenericCrowdsale, LostAndFoundToken, DeploymentInfo, TokenTranchePricing {
  uint public sellable_tokens;

  /*
   * The constructor for the crowdsale was removed given it didn't receive any arguments nor had any body.
   *
   * The configuration from the constructor was moved to the configurationCrowdsale function which creates the token contract and also calls the configuration functions from GenericCrowdsale and TokenTranchePricing.
   * 
   *
   * @param team_multisig Address of the multisignature wallet of the team that will receive all the funds contributed in the crowdsale.
   * @param start Timestamp where the crowdsale will be officially started. It should be greater than the timestamp in which the contract is deployed.
   * @param end Timestamp where the crowdsale finishes. No tokens can be sold through this contract after this timestamp.
   * @param token_retriever Address that will handle tokens accidentally sent to the token contract. See the LostAndFoundToken and CrowdsaleToken contracts for further details.
   */

  function configurationCrowdsale(address team_multisig, uint start, uint end, address token_retriever, uint[] init_tranches, uint multisig_supply, uint crowdsale_supply, uint8 token_decimals, uint max_tokens_to_sell) public onlyOwner {
      // Testing values
      token = new CrowdsaleToken(multisig_supply, token_decimals, team_multisig, token_retriever);
      // Necessary if assignTokens mints
      token.setMintAgent(address(this), true);
      // Necessary if finalize is overriden to release the tokens for public trading.
      token.setReleaseAgent(address(this));
      // Necessary for the execution of buy function and of the subsequent CrowdsaleToken's transfer function. 
      token.setTransferAgent(address(this), true);
      // Crowdsale mints to himself the initial supply
      token.mint(address(this), crowdsale_supply);

      sellable_tokens = max_tokens_to_sell;

      // Configuration functionality for GenericCrowdsale.
      configurationGenericCrowdsale(team_multisig, start, end);

      // Configuration functionality for TokenTranchePricing.
      configurationTokenTranchePricing(init_tranches);
  }

  //TODO: implement token assignation (e.g. through minting or transfer)
  function assignTokens(address receiver, uint tokenAmount) internal {
    token.transfer(receiver, tokenAmount);
  }

  //TODO: implement token amount calculation
  function calculateTokenAmount(uint weiAmount, address) internal view returns (uint weiAllowed, uint tokenAmount) {
    uint tokensPerWei = getCurrentPrice(tokensSold);
    uint maxAllowed = sellable_tokens.sub(tokensSold).div(tokensPerWei);
    weiAllowed = maxAllowed.min256(weiAmount);

    if (weiAmount < maxAllowed) {
      tokenAmount = tokensPerWei.mul(weiAmount);
    }
    // With this case we let the crowdsale end even when there are rounding errors due to the tokens to wei ratio
    else {
      tokenAmount = sellable_tokens.sub(tokensSold);
    }
  }

  //TODO: implement to control funding state criterion
  function isCrowdsaleFull() internal view returns (bool full) {
    return tokensSold >= sellable_tokens;
  }

  /**
   * Finalize a successful crowdsale.
   *
   * The owner can trigger post-crowdsale actions, like releasing the tokens.
   * Note that by default tokens are not in a released state.
   */
  function finalize() public inState(State.Success) onlyOwner stopInEmergency {
    // Uncomment if tokens should be released.
    // token.releaseTokenTransfer();
    super.finalize();
  }

  /**
   * This function decides who handles lost tokens.
   * Do note that this function is NOT meant to be used in a token refund mecahnism.
   * Its sole purpose is determining who can move around ERC20 tokens accidentally sent to this contract.
   */
  function getLostAndFoundMaster() internal view returns (address) {
    return owner;
  }

  // These two setters are present only to correct timestamps if they are off from their target date by more than, say, a day
  // Uncomment only if necessary
  // function setStartingTime(uint startingTime) public onlyOwner inState(State.PreFunding) {
  //     require(startingTime > now && startingTime < endsAt);
  //     startsAt = startingTime;
  // }

  // function setEndingTime(uint endingTime) public onlyOwner notFinished {
  //     require(endingTime > now && endingTime > startsAt);
  //     endsAt = endingTime;
  // }
}