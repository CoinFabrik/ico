pragma solidity ^0.4.8;

import "./Haltable.sol";

/**
 * Forward Ethereum payments to another wallet and track them with an event.
 *
 * Allows to identify customers who made Ethereum payment for a central token issuance.
 * Furthermore allow making a payment on behalf of another address.
 *
 * Allow pausing to signal the end of the crowdsale.
 */
contract PaymentForwarder is Haltable {

  /** Who will get all ETH in the end */
  address public teamMultisig;

  /** Total incoming money */
  uint public totalTransferred;

  /** How many distinct customers we have that have made a payment */
  uint public customerCount;

  /** Total incoming money per centrally tracked customer id */
  mapping(uint128 => uint) public paymentsByCustomer;

  /** Total incoming money per benefactor address */
  mapping(address => uint) public paymentsByBenefactor;

  /** A customer has made a payment. Benefactor is the address where the tokens will be ultimately issued.*/
  event PaymentForwarded(address source, uint amount, uint128 customerId, address benefactor);

  function PaymentForwarder(address _owner, address _teamMultisig) {
    teamMultisig = _teamMultisig;
    owner = _owner;
  }

  /**
   * Pay on a behalf of an address.
   *
   * @param customerId Identifier in the central database, UUID v4
   *
   */
  function pay(uint128 customerId, address benefactor) public stopInEmergency payable {

    uint weiAmount = msg.value;

    PaymentForwarded(msg.sender, weiAmount, customerId, benefactor);

    // We trust Ethereum amounts cannot overflow uint256
    totalTransferred += weiAmount;

    if(paymentsByCustomer[customerId] == 0) {
      customerCount++;
    }

    paymentsByCustomer[customerId] += weiAmount;

    // We track benefactor addresses for extra safety;
    // In the case of central ETH issuance tracking has problems we can
    // construct ETH contributions solely based on blockchain data
    paymentsByBenefactor[benefactor] += weiAmount;

    // May run out of gas
    if(!teamMultisig.send(weiAmount)) throw;
  }

  /**
   * Pay on a behalf of the sender.
   *
   * @param customerId Identifier in the central database, UUID v4
   *
   */
  function payForMyself(uint128 customerId) public payable {
    pay(customerId, msg.sender);
  }

}
