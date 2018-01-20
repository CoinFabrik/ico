pragma solidity ^0.4.18;

/**
 * Authored by https://www.coinfabrik.com/
 */

import "./GenericCrowdsale.sol";
import "./CrowdsaleToken.sol";
import "./LostAndFoundToken.sol";
import "./DeploymentInfo.sol";
import "./TokenTranchePricing.sol";

// This contract has the sole objective of providing a sane concrete instance of the Crowdsale contract.
contract Crowdsale is GenericCrowdsale, LostAndFoundToken, DeploymentInfo, TokenTranchePricing{
  //
  uint private constant token_initial_supply = 85 * (10 ** 6) * (10 ** uint(token_decimals));
  uint8 private constant token_decimals = 18;
  bool private constant token_mintable = true;
  uint private constant sellable_tokens = 340 * (10 ** 6) * (10 ** uint(token_decimals));
  uint public milieurs_per_eth;
  /**
   * Constructor for the crowdsale.
   * Normally, the token contract is created here. That way, the minting, release and transfer agents can be set here too.
   *
   * @param team_multisig Address of the multisignature wallet of the team that will receive all the funds contributed in the crowdsale.
   * @param start Block number where the crowdsale will be officially started. It should be greater than the block number in which the contract is deployed.
   * @param end Block number where the crowdsale finishes. No tokens can be sold through this contract after this block.
   * @param token_retriever Address that will handle tokens accidentally sent to the token contract. See the LostAndFoundToken and CrowdsaleToken contracts for further details.
   */
  function Crowdsale(address team_multisig, uint start, uint end, address token_retriever, uint[] init_tranches, uint mili_eurs_per_eth) GenericCrowdsale(team_multisig, start, end) TokenTranchePricing(init_tranches) public {

    require(end == tranches[tranches.length.sub(1)].end);
    // Testing values
    token = new CrowdsaleToken(token_initial_supply, token_decimals, team_multisig, token_mintable, token_retriever);
    
    // Set permissions to mint, transfer and release
    token.setMintAgent(address(this), true);
    token.setTransferAgent(address(this), true);
    token.setReleaseAgent(address(this));
    
    // Tokens to be sold through this contract
    token.mint(address(this), sellable_tokens);
    
    // We don't need to mint anymore during the lifetime of the contract.
    token.setMintAgent(address(this), false);
    
    //Give multisig permision to send tokens to partners
    token.setTransferAgent(team_multisig, true);

    updateEursPerEth(mili_eurs_per_eth);
  }

  //Token assignation through transfer
  function assignTokens(address receiver, uint tokenAmount) internal{
    token.transfer(receiver, tokenAmount);
  }

  //Token amount calculation
  function calculateTokenAmount(uint weiAmount, address) internal view returns (uint weiAllowed, uint tokenAmount){
    uint tokensPerEth = getCurrentPrice(tokensSold).mul(milieurs_per_eth).div(1000);
    uint maxWeiAllowed = sellable_tokens.sub(tokensSold).mul(1 ether).div(tokensPerEth);
    weiAllowed = maxWeiAllowed.min256(weiAmount);

    if (weiAmount < maxWeiAllowed) {
      //Divided by 1000 because eth eth_price_in_eurs is multiplied by 1000
      tokenAmount = tokensPerEth.mul(weiAmount).div(1 ether);
    }
    // With this case we let the crowdsale end even when there are rounding errors due to the tokens to wei ratio
    else {
      tokenAmount = sellable_tokens.sub(tokensSold);
    }
  }

  // Crowdsale is full once all sellable_tokens are sold.
  function isCrowdsaleFull() internal view returns (bool full) {
    return tokensSold >= sellable_tokens;
  }

  /**
   * Finalize a succcesful crowdsale.
   *
   * The owner can trigger post-crowdsale actions, like releasing the tokens.
   * Note that by default tokens are not in a released state.
   */
  function finalize() public inState(State.Success) onlyOwner stopInEmergency {
    token.releaseTokenTransfer();
    uint unsoldTokens = token.balanceOf(address(this));
    token.burn(address(this), unsoldTokens);
    super.finalize();
  }


  //Change the the starting time in order to end the presale period early if needed.
  function setStartingTime(uint startingTime) public onlyOwner inState(State.PreFunding) {
    require(startingTime > block.timestamp && startingTime < endsAt);
    startsAt = startingTime;
  }

  //Change the the ending time in order to be able to finalize the crowdsale if needed.
  function setEndingTime(uint endingTime) public onlyOwner notFinished {
    require(endingTime > block.timestamp && endingTime > startsAt);
    endsAt = endingTime;
  }

  /**
   * This function decides who handles lost tokens.
   * Do note that this function is NOT meant to be used in a token refund mecahnism.
   * Its sole purpose is determining who can move around ERC20 tokens accidentally sent to this contract.
   */
  function getLostAndFoundMaster() internal view returns (address) {
    return owner;
  }
  
  //Update ETH value in milieurs
  function updateEursPerEth (uint milieurs_amount) public onlyOwner {
    require(milieurs_amount >= 100);
    milieurs_per_eth = milieurs_amount;
  }
  /**
   * Override to reject calls unless the crowdsale is finalized or
   *  the token contract is not the one corresponding to this crowdsale
   */
  function enableLostAndFound(address agent, uint tokens, EIP20Token token_contract) public {
    // Either the state is finalized or the token_contract is not this crowdsale token
    require(address(token_contract) != address(token) || getState() == State.Finalized);
    super.enableLostAndFound(agent, tokens, token_contract);
  }
}
