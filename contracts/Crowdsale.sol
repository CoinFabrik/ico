pragma solidity ^0.4.19;

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
  uint public initial_tokens;
  uint public milieurs_per_eth;
  // Minimum amounts of tokens that must be bought by an investor
  uint public minimum_buy_value;
  address public price_agent; 

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

  function configurationCrowdsale(address team_multisig, uint start, uint end,
  address token_retriever, uint[] init_tranches, uint multisig_supply, uint crowdsale_supply,
  uint8 token_decimals, uint max_tokens_to_sell) public onlyOwner {

    initial_tokens = multisig_supply;
    minimum_buy_value = uint(100).mul(10 ** uint(token_decimals));
    token = new CrowdsaleToken(multisig_supply, token_decimals, team_multisig, token_retriever);
    // Necessary if assignTokens mints
    token.setMintAgent(address(this), true);
    // Necessary if finalize is overriden to release the tokens for public trading.
    token.setReleaseAgent(address(this));
    // Necessary for the execution of buy function and of the subsequent CrowdsaleToken's transfer function. 
    token.setTransferAgent(address(this), true);
    // Necessary for the delivery of bounties 
    token.setTransferAgent(team_multisig, true);
    // Crowdsale mints to himself the initial supply
    token.mint(address(this), crowdsale_supply);
    // Necessary if assignTokens mints
    token.setMintAgent(address(this), false);

    sellable_tokens = max_tokens_to_sell;

    // Configuration functionality for GenericCrowdsale.
    configurationGenericCrowdsale(team_multisig, start, end);

    // Configuration functionality for TokenTranchePricing.
    configurationTokenTranchePricing(init_tranches);
  }

  //token assignation
  function assignTokens(address receiver, uint tokenAmount) internal {
    token.transfer(receiver, tokenAmount);
  }

  //token amount calculation
  function calculateTokenAmount(uint weiAmount, address receiver) internal view returns (uint weiAllowed, uint tokenAmount) {
    //Divided by 1000 because eth eth_price_in_eurs is multiplied by 1000
    uint tokensPerEth = getCurrentPrice(tokensSold).mul(milieurs_per_eth).div(1000);
    uint maxWeiAllowed = sellable_tokens.sub(tokensSold).mul(1 ether).div(tokensPerEth);
    weiAllowed = maxWeiAllowed.min256(weiAmount);

    if (weiAmount < maxWeiAllowed) {
      tokenAmount = tokensPerEth.mul(weiAmount).div(1 ether);
    }
    // With this case we let the crowdsale end even when there are rounding errors due to the tokens to wei ratio
    else {
      tokenAmount = sellable_tokens.sub(tokensSold);
    }

    // Require a minimum contribution of 100 fulltokens
    require(token.balanceOf(receiver).add(tokenAmount) >= minimum_buy_value);
  }

  // Implements funding state criterion
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
    //Tokens sold + bounties represent 82% of the total, the other 18% goes to the multisig, partners and market making
    uint sold = tokensSold.add(initial_tokens);
    uint toShare = sold.mul(18).div(82);

    // Mint the 18% to the multisig
    token.setMintAgent(address(this), true);
    token.mint(multisigWallet, toShare);
    token.setMintAgent(address(this), false);

    // Release transfers and burn unsold tokens.
    token.releaseTokenTransfer();
    token.burn(token.balanceOf(address(this)));

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
  function setStartingTime(uint startingTime) public onlyOwner inState(State.PreFunding) {
    require(now < startingTime && startingTime < endsAt);
    startsAt = startingTime;
  }

  function setEndingTime(uint endingTime) public onlyOwner notFinished {
    require(now < endingTime && startsAt < endingTime);
    endsAt = endingTime;
  }

  function updateEursPerEth (uint milieurs_amount) public notFinished {
    require(milieurs_amount >= 100);
    require(msg.sender == price_agent);
    milieurs_per_eth = milieurs_amount;
  }

  function updatePriceAgent(address new_price_agent) public onlyOwner notFinished {
    price_agent = new_price_agent;
  }

  /**
   * @param new_minimum New minimum amount of indivisible tokens to be required
   */
  function setMinimumBuyValue(uint new_minimum) public onlyOwner notFinished {
    minimum_buy_value = new_minimum;
  }
}