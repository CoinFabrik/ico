pragma solidity ^0.4.18;

/**
 * Authored by https://www.coinfabrik.com/
 */

import "./GenericCrowdsale.sol";
import "./CrowdsaleToken.sol";
import "./LostAndFoundToken.sol";
import "./TokenTranchePricing.sol";
import "./DeploymentInfo.sol";

// This contract has the sole objective of providing a sane concrete instance of the Crowdsale contract.
contract Crowdsale is GenericCrowdsale, LostAndFoundToken, TokenTranchePricing {
  //initial supply in 400k, sold tokens from initial minting
  uint8 private constant token_decimals = 18;
  uint private constant token_initial_supply = 4 * (10 ** 5) * (10 ** uint(token_decimals));
  bool private constant token_mintable = true;
  uint private constant sellable_tokens = 6 * (10 ** 5) * (10 ** uint(token_decimals));
  
  //Sets minimum value that can be bought
  uint public minimum_buy_value = 175 * 1 ether / 100;
  //Eth price multiplied by 1000;
  uint public eurs_per_eth;


  /**
   * Constructor for the crowdsale.
   * Normally, the token contract is created here. That way, the minting, release and transfer agents can be set here too.
   *
   * @param eth_price_in_eurs Ether price in EUR.
   * @param team_multisig Address of the multisignature wallet of the team that will receive all the funds contributed in the crowdsale.
   * @param start Block number where the crowdsale will be officially started. It should be greater than the block number in which the contract is deployed.
   * @param end Block number where the crowdsale finishes. No tokens can be sold through this contract after this block.
   * @param token_retriever Address that will handle tokens accidentally sent to the token contract. See the LostAndFoundToken and CrowdsaleToken contracts for further details.
   * @param init_tranches List of serialized tranches. See config.js and TokenTranchePricing for further details.
   */
  function Crowdsale(uint eth_price_in_eurs, address team_multisig, uint start, uint end, address token_retriever, uint[] init_tranches)
  GenericCrowdsale(team_multisig, start, end) TokenTranchePricing(init_tranches) public {
    require(end == tranches[tranches.length.sub(1)].end);
    // Testing values
    token = new CrowdsaleToken(token_initial_supply, token_decimals, team_multisig, token_mintable, token_retriever);
    
    //Set eth price in EUR (multiplied by one thousand)
    updateEursPerEth(eth_price_in_eurs);

    // Set permissions to mint, transfer and release
    token.setMintAgent(address(this), true);
    token.setTransferAgent(address(this), true);
    token.setReleaseAgent(address(this));

    // Allow the multisig to transfer tokens
    token.setTransferAgent(team_multisig, true);

    // Tokens to be sold through this contract
    token.mint(address(this), sellable_tokens);
    // We don't need to mint anymore during the lifetime of the contract.
    token.setMintAgent(address(this), false);
  }

  //Token assignation through transfer
  function assignTokens(address receiver, uint tokenAmount) internal {
    token.transfer(receiver, tokenAmount);
  }

  //Token amount calculation
  function calculateTokenAmount(uint weiAmount, address) internal view returns (uint weiAllowed, uint tokenAmount) {
    uint tokensPerWei = getCurrentPrice(tokensSold).mul(eurs_per_eth);
    uint maxAllowed = sellable_tokens.sub(tokensSold).div(tokensPerWei);
    weiAllowed = maxAllowed.min256(weiAmount);

    if (weiAmount < maxAllowed) {
      //Divided by 1000 because eth eth_price_in_eurs is multiplied by 1000
      tokenAmount = tokensPerWei.mul(weiAmount).div(1000);
    }
    // With this case we let the crowdsale end even when there are rounding errors due to the tokens to wei ratio
    else {
      tokenAmount = sellable_tokens.sub(tokensSold);
    }
  }

  // Implements the criterion of the funding state
  function isCrowdsaleFull() internal view returns (bool) {
    return tokensSold >= sellable_tokens;
  }

  /**
   * This function decides who handles lost tokens.
   * Do note that this function is NOT meant to be used in a token refund mechanism.
   * Its sole purpose is determining who can move around ERC20 tokens accidentally sent to this contract.
   */
  function getLostAndFoundMaster() internal view returns (address) {
    return owner;
  }

  /**
   * @dev Sets new minimum buy value for a transaction. Only the owner can call it.
   */
  function setMinimumBuyValue(uint newValue) public onlyOwner {
    minimum_buy_value = newValue;
  }

  /**
   * Investing function that recognizes the payer and verifies that he is allowed to invest.
   *
   * Overwritten to add configurable minimum value
   *
   * @param customerId UUIDv4 that identifies this contributor
   */
  function buyWithSignedAddress(uint128 customerId, uint8 v, bytes32 r, bytes32 s) public payable investmentIsBigEnough(msg.sender) validCustomerId(customerId) {
    super.buyWithSignedAddress(customerId, v, r, s);
  }


  /**
   * Investing function that recognizes the payer.
   * 
   * @param customerId UUIDv4 that identifies this contributor
   */
  function buyWithCustomerId(uint128 customerId) public payable investmentIsBigEnough(msg.sender) validCustomerId(customerId) unsignedBuyAllowed {
    super.buyWithCustomerId(customerId);
  }

  /**
   * The basic entry point to participate in the crowdsale process.
   *
   * Pay for funding, get invested tokens back in the sender address.
   */
  function buy() public payable investmentIsBigEnough(msg.sender) unsignedBuyAllowed {
    super.buy();
  }

  // Extended to transfer half of the unused funds to the team's multisig and release the token
  function finalize() public inState(State.Success) onlyOwner stopInEmergency {
    token.releaseTokenTransfer();
    uint unsoldTokens = token.balanceOf(address(this));
    token.burn(unsoldTokens.div(2));
    token.transfer(multisigWallet, unsoldTokens - unsoldTokens.div(2));
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
   * Override to reject calls unless the crowdsale is finalized or
   *  the token contract is not the one corresponding to this crowdsale
   */
  function enableLostAndFound(address agent, uint tokens, EIP20Token token_contract) public {
    // Either the state is finalized or the token_contract is not this crowdsale token
    require(address(token_contract) != address(token) || getState() == State.Finalized);
    super.enableLostAndFound(agent, tokens, token_contract);
  }

  function updateEursPerEth (uint eurs_amount) public onlyOwner {
    require(eurs_amount >= 100);
    eurs_per_eth = eurs_amount;
  }


  modifier investmentIsBigEnough(address agent) {
    require(msg.value.add(investedAmountOf[agent]) >= minimum_buy_value);
    _;
  }
}