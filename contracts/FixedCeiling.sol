pragma solidity ^0.4.11;

import "./SafeMath.sol";
import "./Ownable.sol";
import "./CeilingStrategy.sol";

contract FixedCeiling is CeilingStrategy {
    using SafeMath for uint;

    uint public chunkedWeiMultiple;
    uint public weiLimitPerAddress;

    function FixedCeiling(uint multiple, uint limit) {
        chunkedWeiMultiple = multiple;
        weiLimitPerAddress = limit;
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

    function relaxFundingCap(uint newCap, uint weiRaised) public constant returns (uint) {
        if (newCap > weiRaised) return newCap;
        else return weiRaised.div(chunkedWeiMultiple).add(1).mul(chunkedWeiMultiple);
    }

}