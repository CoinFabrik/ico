pragma solidity ^0.4.13;

/**
 * Originally from https://github.com/TokenMarketNet/ico
 * Modified by https://www.coinfabrik.com/
 */

import "./Haltable.sol";
import "./SafeMath.sol";
import "./PricingStrategy.sol";
import "./FinalizeAgent.sol";
import "./CeilingStrategy.sol";
import "./HagglinToken.sol";

/**
 * Abstract base contract for token sales.
 *
 * Handles
 * - start and end dates
 * - accepting investments
 * - minimum funding goal and refund
 * - various statistics during the crowdfund
 * - different pricing strategies
 * - different investment policies (require server side customer id, allow only whitelisted addresses)
 *
 * Concrete implementations should provide a valid public constructor and assignToken function.
 */
contract Crowdsale is Haltable {

  using SafeMath for uint;

  /* The token we are selling */
  HagglinToken public token;

  /* How we are going to price our offering */
  PricingStrategy public pricingStrategy;

  /* How we are going to limit our offering */
  CeilingStrategy public ceilingStrategy;

  /* Post-success callback */
  FinalizeAgent public finalizeAgent;

  /* ether will be transferred to this address */
  address public multisigWallet;

  /* if the funding goal is not reached, investors may withdraw their funds */
  uint public minimumFundingGoal;

  /* the funding cannot exceed this cap; may be set later on during the crowdsale */
  uint public weiFundingCap = 0;

  /* the starting block number of the crowdsale */
  uint public startsAt;

  /* the ending block number of the crowdsale */
  uint public endsAt;

  /* the number of tokens already sold through this contract*/
  uint public tokensSold = 0;

  /* How many wei of funding we have raised */
  uint public weiRaised = 0;

  /* How many distinct addresses have invested */
  uint public investorCount = 0;

  /* How many wei we have returned back to the contract after a failed crowdfund. */
  uint public loadedRefund = 0;

  /* How many wei we have given back to investors.*/
  uint public weiRefunded = 0;

  /* Has this crowdsale been finalized */
  bool public finalized;

  /* Do we need to have a unique contributor id for each customer */
  bool public requireCustomerId;

  /** How many ETH each address has invested in this crowdsale */
  mapping (address => uint) public investedAmountOf;

  /** How many tokens this crowdsale has credited for each investor address */
  mapping (address => uint) public tokenAmountOf;

  /** Addresses that are allowed to invest even before ICO offical opens. For testing, for ICO partners, etc. */
  mapping (address => bool) public earlyParticipantWhitelist;

  /** This is for manual testing of the interaction with the owner's wallet. You can set it to any value and inspect this in a blockchain explorer to see that crowdsale interaction works. */
  uint8 public ownerTestValue;

  /** State machine
   *
   * - Prefunding: We have not reached the starting block yet
   * - Funding: Active crowdsale
   * - Success: Minimum funding goal reached
   * - Failure: Minimum funding goal not reached before the ending block
   * - Finalized: The finalize function has been called and succesfully executed
   * - Refunding: Refunds are loaded on the contract to be reclaimed by investors.
   */
  enum State{Unknown, PreFunding, Funding, Success, Failure, Finalized, Refunding}


  // A new investment was made
  event Invested(address investor, uint weiAmount, uint tokenAmount, uint128 customerId);

  // Refund was processed for a contributor
  event Refund(address investor, uint weiAmount);

  // The rules about what kind of investments we accept were changed
  event InvestmentPolicyChanged(bool requireCId);

  // Address early participation whitelist status changed
  event Whitelisted(address addr, bool status);

  // Crowdsale's finalize function has been called
  event Finalized();

  // A new funding cap has been set
  event FundingCapSet(uint newFundingCap);

  function Crowdsale(address _multisigWallet, uint _start, uint _end, uint _minimumFundingGoal) internal {
    setMultisig(_multisigWallet);

    // Don't mess the dates
    require(_start != 0 && _end != 0);
    require(block.number < _start && _start < _end);
    startsAt = _start;
    endsAt = _end;

    // Minimum funding goal can be zero
    minimumFundingGoal = _minimumFundingGoal;
  }

  /**
   * Concrete implementations of the crowdsale should decide how the tokens are assigned (e.g. through minting or transfer)
   */
  function assignTokens(address receiver, uint tokenAmount) internal;

  /**
   * Don't expect to just send in money and get tokens.
   */
  function() payable {
    require(false);
  }

  /**
   * Make an investment.
   *
   * Crowdsale must be running for one to invest.
   * We must have not pressed the emergency brake.
   *
   * @param receiver The Ethereum address who receives the tokens
   * @param customerId (optional) UUID v4 to track the successful payments on the server side
   *
   */
  function investInternal(address receiver, uint128 customerId) stopInEmergency notFinished private {
    // Determine if it's a good time to accept investment from this participant
    if (getState() == State.PreFunding) {
      // Are we whitelisted for early deposit
      require(earlyParticipantWhitelist[receiver]);
    }

    uint weiAmount = ceilingStrategy.weiAllowedToReceive(msg.value, weiRaised, investedAmountOf[receiver], weiFundingCap);
    uint tokenAmount = pricingStrategy.calculatePrice(weiAmount, weiRaised, tokensSold, msg.sender, token.decimals());
    
    // Dust transaction if no tokens can be given
    require(tokenAmount != 0);

    if (investedAmountOf[receiver] == 0) {
      // A new investor
      investorCount++;
    }
    updateInvestorFunds(tokenAmount, weiAmount, receiver, customerId);

    // Pocket the money
    multisigWallet.transfer(weiAmount);

    // Return excess of money
    uint weiToReturn = msg.value.sub(weiAmount);
    if (weiToReturn > 0) {
      msg.sender.transfer(weiToReturn);
    }
  }

  /**
   * Preallocate tokens for the early investors.
   *
   * Preallocated tokens have been sold before the actual crowdsale opens.
   * This function mints the tokens and moves the crowdsale needle.
   *
   * No money is exchanged, as the crowdsale team already have received the payment.
   *
   * @param fullTokens tokens as full tokens - decimal places added internally
   * @param weiPrice Price of a single full token in wei
   *
   */
  function preallocate(address receiver, uint fullTokens, uint weiPrice) public onlyOwner notFinished {
    require(receiver != address(0));
    uint tokenAmount = fullTokens.mul(10**uint(token.decimals()));
    require(tokenAmount != 0);
    uint weiAmount = weiPrice.mul(tokenAmount); // This can also be 0, in which case we give out tokens for free
    updateInvestorFunds(tokenAmount, weiAmount, receiver , 0);
  }

  /**
   * Private function to update accounting in the crowdsale.
   */
  function updateInvestorFunds(uint tokenAmount, uint weiAmount, address receiver, uint128 customerId) private {
    // Update investor
    investedAmountOf[receiver] = investedAmountOf[receiver].add(weiAmount);
    tokenAmountOf[receiver] = tokenAmountOf[receiver].add(tokenAmount);

    // Update totals
    weiRaised = weiRaised.add(weiAmount);
    tokensSold = tokensSold.add(tokenAmount);

    assignTokens(receiver, tokenAmount);
    // Tell us that the investment was completed successfully
    Invested(receiver, weiAmount, tokenAmount, customerId);
  }


  /**
   * Allow the owner to set a funding cap on the crowdsale.
   * The new cap should be higher than the minimum funding goal.
   * 
   * @param newCap minimum target cap that may be relaxed if it was already broken.
   */
  function setFundingCap(uint newCap) public onlyOwner notFinished {
    weiFundingCap = ceilingStrategy.relaxFundingCap(newCap, weiRaised);
    require(weiFundingCap >= minimumFundingGoal);
    FundingCapSet(weiFundingCap);
  }

  /**
   * Invest to tokens, recognize the payer.
   *
   */
  function buyWithCustomerId(uint128 customerId) public payable {
    require(customerId != 0);  // UUIDv4 sanity check
    investInternal(msg.sender, customerId);
  }

  /**
   * The basic entry point to participate in the crowdsale process.
   *
   * Pay for funding, get invested tokens back in the sender address.
   */
  function buy() public payable {
    require(!requireCustomerId); // Crowdsale needs to track participants for thank you email
    investInternal(msg.sender, 0);
  }

  /**
   * Finalize a succcesful crowdsale.
   *
   * The owner can trigger a call the contract that provides post-crowdsale actions, like releasing the tokens.
   */
  function finalize() public inState(State.Success) onlyOwner stopInEmergency {
    finalizeAgent.finalizeCrowdsale(token);
    finalized = true;
    Finalized();
  }

  /**
   * Set policy do we need to have server-side customer ids for the investments.
   *
   */
  function setRequireCustomerId(bool value) public onlyOwner stopInEmergency {
    requireCustomerId = value;
    InvestmentPolicyChanged(requireCustomerId);
  }

  /**
   * Allow addresses to do early participation.
   *
   */
  function setEarlyParticipantWhitelist(address addr, bool status) public onlyOwner notFinished stopInEmergency {
    earlyParticipantWhitelist[addr] = status;
    Whitelisted(addr, status);
  }

  /**
   * Allow to (re)set pricing strategy.
   */
  function setPricingStrategy(PricingStrategy addr) internal {
    // Disallow setting a bad agent
    require(addr.isPricingStrategy());
    pricingStrategy = addr;
  }

  /**
   * Allow to (re)set ceiling strategy.
   */
  function setCeilingStrategy(CeilingStrategy addr) internal {
    // Disallow setting a bad agent
    require(addr.isCeilingStrategy());
    ceilingStrategy = addr;
  }

  /**
   * Allow to (re)set finalize agent.
   */
  function setFinalizeAgent(FinalizeAgent addr) internal {
    // Disallow setting a bad agent
    require(addr.isFinalizeAgent());
    finalizeAgent = addr;
    require(isFinalizerSane());
  }

  /**
   * Internal setter for the multisig wallet
   */
  function setMultisig(address addr) internal {
    require(addr != 0);
    multisigWallet = addr;
  }

  /**
   * Allow load refunds back on the contract for the refunding.
   *
   * The team can transfer the funds back on the smart contract in the case that the minimum goal was not reached.
   */
  function loadRefund() public payable inState(State.Failure) stopInEmergency {
    require(msg.value >= weiRaised);
    require(weiRefunded == 0);
    uint excedent = msg.value.sub(weiRaised);
    loadedRefund = loadedRefund.add(msg.value.sub(excedent));
    investedAmountOf[msg.sender].add(excedent);
  }

  /**
   * Investors can claim refund.
   */
  function refund() public inState(State.Refunding) stopInEmergency {
    uint weiValue = investedAmountOf[msg.sender];
    require(weiValue != 0);
    investedAmountOf[msg.sender] = 0;
    weiRefunded = weiRefunded.add(weiValue);
    Refund(msg.sender, weiValue);
    msg.sender.transfer(weiValue);
  }

  /**
   * @return true if the crowdsale has raised enough money to be a success
   */
  function isMinimumGoalReached() public constant returns (bool reached) {
    return weiRaised >= minimumFundingGoal;
  }

  /**
   * Check if the contract relationship looks good.
   */
  function isFinalizerSane() public constant returns (bool sane) {
    return finalizeAgent.isSane(token);
  }

  /**
   * Crowdfund state machine management.
   *
   * This function has the timed transition builtin.
   * So there is no chance of the variable being stale.
   */
  function getState() public constant returns (State) {
    if (finalized) return State.Finalized;
    else if (block.number < startsAt) return State.PreFunding;
    else if (block.number <= endsAt && !ceilingStrategy.isCrowdsaleFull(weiRaised, weiFundingCap)) return State.Funding;
    else if (isMinimumGoalReached()) return State.Success;
    else if (!isMinimumGoalReached() && weiRaised > 0 && loadedRefund >= weiRaised) return State.Refunding;
    else return State.Failure;
  }

  /** This is for manual testing of multisig wallet interaction */
  function setOwnerTestValue(uint8 val) public onlyOwner stopInEmergency {
    ownerTestValue = val;
  }

  /** Interface marker. */
  function isCrowdsale() public constant returns (bool) {
    return true;
  }

  //
  // Modifiers
  //

  /** Modifier allowing execution only if the crowdsale is currently running.  */
  modifier inState(State state) {
    require(getState() == state);
    _;
  }

  modifier notFinished() {
    State current_state = getState();
    require(current_state == State.PreFunding || current_state == State.Funding);
    _;
  }

}