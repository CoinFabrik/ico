pragma solidity ^0.4.15;

import "./GenericCrowdsale.sol";
import "./CrowdsaleToken.sol";
import "./LostAndFoundToken.sol";

// This contract has the sole objective of providing a sane concrete instance of the Crowdsale contract.
contract Crowdsale is GenericCrowdsale, LostAndFoundToken {
  uint private constant token_initial_supply = 1;
  uint8 private constant token_decimals = 15;
  bool private constant token_mintable = true;
  
  //Sets minimum value that can be bought
  uint private minimum_buy_value = 1;
  
  function Crowdsale(address team_multisig, uint start, uint end, address token_retriever) GenericCrowdsale(team_multisig, start, end) public {
      // Testing values
      token = new CrowdsaleToken(token_initial_supply, token_decimals, team_multisig, token_mintable, token_retriever);
      // Necessary if assignTokens mints
      // token.setMintAgent(address(this), true);
  }

  //TODO: implement token assignation (e.g. through minting or transfer)
  function assignTokens(address receiver, uint tokenAmount) internal;

  //TODO: implement token amount calculation
  function calculateTokenAmount(uint weiAmount, address agent) internal constant returns (uint weiAllowed, uint tokenAmount);

  //TODO: implement to control funding state criteria
  function isCrowdsaleFull() internal constant returns (bool full);

  /**
   * This function decides who handles lost tokens.
   * Do note that this function is NOT meant to be used in a token refund mecahnism.
   * Its sole purpose is determining who can move around ERC20 tokens accidentally sent to this contract.
   */
  function getLostAndFoundMaster() internal constant returns (address) {
    return owner;
  }

  /**
   * Sets new minimum buy. Only the owner can call it
   */

  function setMininmumBuyValue(uint newValue) public onlyOwner {
    minimum_buy_value = newValue;
  }

  /**
   * Investing function that recognizes the payer and verifies he is allowed to invest.
   *
   * Overwritten to add configurable minimum value
   *
   * @param customerId UUIDv4 that identifies this contributor
   */
  function buyWithSignedAddress(uint128 customerId, uint8 v, bytes32 r, bytes32 s) public payable validCustomerId(customerId) {
    require(msg.value >= minimum_buy_value);
    super.buyWithSignedAddress(customerId, v, r, s);
  }


  /**
   * Investing function that recognizes the payer.
   * 
   * @param customerId UUIDv4 that identifies this contributor
   */
  function buyWithCustomerId(uint128 customerId) public payable validCustomerId(customerId) unsignedBuyAllowed {
    require(msg.value >= minimum_buy_value);
    super.buyWithCustomerId(customerId) ;
  }

  /**
   * The basic entry point to participate in the crowdsale process.
   *
   * Pay for funding, get invested tokens back in the sender address.
   */
  function buy() public payable unsignedBuyAllowed {
    require(msg.value >= minimum_buy_value);
    super.buy();
  }
}