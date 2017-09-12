pragma solidity ^0.4.13;

import "./CappedCrowdsale.sol";
import "./CrowdsaleToken.sol";
import "./FixedCeiling.sol";
import "./BonusFinalizeAgent.sol";

// This contract has the sole objective of providing a sane concrete instance of the Crowdsale contract.
contract Crowdsale is CappedCrowdsale {
  uint private constant chunked_multiple = 10000 * (10 ** 18); // in wei
  uint private constant limit_per_address = 100000 * (10 ** 18); // in wei
  uint private constant minimum_funding = 0 * (10 ** 18); // in wei

  uint private constant token_initial_supply = 0;
  uint8 private constant token_decimals = 16;
  bool private constant token_mintable = true;
  string private constant token_name = "BurgerKoenig";
  string private constant token_symbol = "BK";

  uint private constant bonus_base_points = 0;
  uint private constant fundingCap = uint(100000000 * (10 ** 18)) / 2700;


  uint private constant decimalTokensPerWei2Eth = 25;
  uint private constant decimalTokensPerWei20Eth = 26;
  uint private constant decimalTokensPerWei50Eth = 27;

  mapping (address => bool) public discountedInvestors;


  function Crowdsale(address team_multisig, uint start, uint end) GenericCrowdsale(team_multisig, start, end, minimum_funding) public {
    // Testing values
    token = new CrowdsaleToken(token_name, token_symbol, token_initial_supply, token_decimals, team_multisig, token_mintable);
    token.setMintAgent(address(this), true);
    setFundingCap(fundingCap);
  }

  function assignTokens(address receiver, uint tokenAmount) internal {
    token.mint(receiver, tokenAmount);
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

  modifier notLessThan2Eth() {
    require(investedAmountOf[msg.sender].add(msg.value) >= 2 * (10**18));   
    _;
  }

  function calculatePrice(uint weiAmount, address customer) internal constant returns (uint) {
    uint investedAmount = investedAmountOf[customer].add(weiAmount);
    uint decimalTokensPerWei;
    if (investedAmount <= 20 * (10**18) && !discountedInvestors[customer]) {
      decimalTokensPerWei = decimalTokensPerWei2Eth;
    } else if (investedAmount <= 50 * (10**18)) {
      decimalTokensPerWei = decimalTokensPerWei20Eth;
    } else {
      decimalTokensPerWei = decimalTokensPerWei50Eth;
    }
    uint decimalTokens = weiAmount.mul(decimalTokensPerWei);
    return decimalTokens;
  }

  function buy() public payable notLessThan2Eth {
    super.buy();
  }

  function setDiscountedInvestor(address addr, bool status) public onlyOwner notFinished stopInEmergency {
    discountedInvestors[addr] = status;
  } 

  function weiAllowedToReceive(uint tentativeAmount, address) internal constant returns (uint) {
      // Then, we check the funding cap
      if (weiFundingCap == 0) return tentativeAmount;
      uint total = tentativeAmount.add(weiRaised);
      if (total < weiFundingCap) return tentativeAmount;
      else return weiFundingCap.sub(weiRaised);
  }

  function isCrowdsaleFull() internal constant returns (bool) {
      return weiFundingCap > 0 && weiRaised >= weiFundingCap;
  }
}