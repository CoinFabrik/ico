pragma solidity ^0.4.15;

import "./GenericCrowdsale.sol";
import "./CrowdsaleToken.sol";
import "./LostAndFoundToken.sol";
import "./TokenTranchePricing.sol";

// This contract has the sole objective of providing a sane concrete instance of the Crowdsale contract.
contract Crowdsale is GenericCrowdsale, LostAndFoundToken, TokenTranchePricing {
  //initial supply in 400k, sold tokens from initial minting
  uint private constant token_initial_supply = 4 * (10 ** 5) * (10 ** uint(token_decimals));
  uint8 private constant token_decimals = 15;
  bool private constant token_mintable = true;
  uint private constant sellable_tokens = 6 * (10 ** 5) * (10 ** uint(token_decimals));
  
  //Sets minimum value that can be bought
  uint private minimum_buy_value = 1;
  
  function Crowdsale(address team_multisig, uint start, uint end, address token_retriever) GenericCrowdsale(team_multisig, start, end) public {
      // Testing values
      token = new CrowdsaleToken(token_initial_supply, token_decimals, team_multisig, token_mintable, token_retriever);

      //Tokens to be sold through this contract
      token.mint(address(this), sellable_tokens);
  }

  //Token assignation through trasfer
  function assignTokens(address receiver, uint tokenAmount) internal{
    token.transfer(receiver, tokenAmount);
  }

  //Token amount calculation
  function calculateTokenAmount(uint weiAmount, address agent) internal constant returns (uint weiAllowed, uint tokenAmount){
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

  //TODO: implement to control funding state criteria
  function isCrowdsaleFull() internal constant returns (bool) {
    return tokensSold >= sellable_tokens;
  }

  /**
   * This function decides who handles lost tokens.
   * Do note that this function is NOT meant to be used in a token refund mecahnism.
   * Its sole purpose is determining who can move around ERC20 tokens accidentally sent to this contract.
   */
  function getLostAndFoundMaster() internal constant returns (address) {
    return owner;
  }

  /**
   * @dev Sets new minimum buy value for a transaction. Only the owner can call it
   */
  function setMinimumBuyValue(uint newValue) public onlyOwner {
    minimum_buy_value = newValue;
  }

  /**
   * Investing function that recognizes the payer and verifies he is allowed to invest.
   *
   * Overwritten to add configurable minimum value
   *
   * @param customerId UUIDv4 that identifies this contributor
   */
  function buyWithSignedAddress(uint128 customerId, uint8 v, bytes32 r, bytes32 s) public payable valueIsBigEnough validCustomerId(customerId) {
    super.buyWithSignedAddress(customerId, v, r, s);
  }


  /**
   * Investing function that recognizes the payer.
   * 
   * @param customerId UUIDv4 that identifies this contributor
   */
  function buyWithCustomerId(uint128 customerId) public payable valueIsBigEnough validCustomerId(customerId) unsignedBuyAllowed {
    super.buyWithCustomerId(customerId) ;
  }

  /**
   * The basic entry point to participate in the crowdsale process.
   *
   * Pay for funding, get invested tokens back in the sender address.
   */
  function buy() public payable valueIsBigEnough unsignedBuyAllowed {
    super.buy();
  }

  //Extended to trasfer unused funds to team team_multisig
  function finalize() public inState(State.Success) onlyOwner stopInEmergency {
    uint unspentTokens = sellable_tokens.sub(tokensSold);
    token.transfer(multisigWallet, unspentTokens);
    super.finalize();
  }

  modifier valueIsBigEnough() {
    require(msg.value >= minimum_buy_value);
    _;
  }
}