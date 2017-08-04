pragma solidity ^0.4.14;

import "./SafeMath.sol";
import "./CeilingStrategy.sol";

/**
 * Fixed cap investment per address and crowdsale
 */
contract FixedCeiling is CeilingStrategy {
    using SafeMath for uint;

    /* When relaxing a cap is necessary, we use this multiple to determine the relaxed cap */
    uint public chunkedWeiMultiple;
    /* The limit an individual address can invest */
    uint public weiLimitPerAddress;

    function FixedCeiling(uint multiple, uint limit) {
        chunkedWeiMultiple = multiple;
        weiLimitPerAddress = limit;
    }

    function isSane(Crowdsale crowdsale) public constant returns (bool) {
        return address(crowdsale.ceilingStrategy()) == address(this);
    }

    function weiAllowedToReceive(uint tentativeAmount, uint weiRaised, uint weiInvestedBySender, uint weiFundingCap) public constant returns (uint) {
        // First, we limit per address investment
        uint totalOfSender = tentativeAmount.add(weiInvestedBySender);
        if (totalOfSender > weiLimitPerAddress) tentativeAmount = weiLimitPerAddress.sub(weiInvestedBySender);
        // Then, we check the funding cap
        if (weiFundingCap == 0) return tentativeAmount;
        uint total = tentativeAmount.add(weiRaised);
        if (total < weiFundingCap) return tentativeAmount;
        else return weiFundingCap.sub(weiRaised);
    }

    function isCrowdsaleFull(uint weiRaised, uint weiFundingCap) public constant returns (bool) {
        return weiFundingCap > 0 && weiRaised >= weiFundingCap;
    }

    /* If the new target cap has not been reached yet, it's fine as it is */
    function relaxFundingCap(uint newCap, uint weiRaised) public constant returns (uint) {
        if (newCap > weiRaised) return newCap;
        else return weiRaised.div(chunkedWeiMultiple).add(1).mul(chunkedWeiMultiple);
    }

}