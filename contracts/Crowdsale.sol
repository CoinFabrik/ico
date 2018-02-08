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
contract Crowdsale is GenericCrowdsale, LostAndFoundToken, DeploymentInfo, TokenTranchePricing {
  uint private constant token_initial_supply = 1;
  uint8 private constant token_decimals = 15;
  bool private constant token_mintable = true;
  uint private constant sellable_tokens = 525 * (10 ** 5) * (10 ** uint(token_decimals));

  /*
   * Constructor for the crowdsale.
   * Normally, the token contract is created here. That way, the minting, release and transfer agents can be set here too.
   *
   * @param team_multisig Address of the multisignature wallet of the team that will receive all the funds contributed in the crowdsale.
   * @param start Block number where the crowdsale will be officially started. It should be greater than the block number in which the contract is deployed.
   * @param end Block number where the crowdsale finishes. No tokens can be sold through this contract after this block.
   * @param token_retriever Address that will handle tokens accidentally sent to the token contract. See the LostAndFoundToken and CrowdsaleToken contracts for further details.
   */
  function Crowdsale() GenericCrowdsale() TokenTranchePricing() public {
      
  }

  function configurationCrowdsale(address team_multisig, uint start, uint end, address token_retriever, uint[] init_tranches) public {
      // Testing values
      token = new CrowdsaleToken(token_initial_supply, token_decimals, team_multisig, token_mintable, token_retriever);
      // Necessary if assignTokens mints
      // token.setMintAgent(address(this), true);
      // Necessary if finalize is overriden to release the tokens for public trading.
      // token.setReleaseAgent(address(this));

      configurationGenericCrowdsale(team_multisig, start, end);

      configurationTokenTranchePricing(init_tranches);
  }

  //TODO: implement token assignation (e.g. through minting or transfer)
  function assignTokens(address receiver, uint tokenAmount) internal {
    token.transfer(receiver, tokenAmount)
  }

  //TODO: implement token amount calculation
  function calculateTokenAmount(uint weiAmount, address receiver) internal view returns (uint weiAllowed, uint tokenAmount) {
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
   * Finalize a succcesful crowdsale.
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