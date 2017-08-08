pragma solidity ^0.4.13;

import "./Crowdsale.sol";
import "./CrowdsaleToken.sol";
import "./FlatPricing.sol";
import "./FixedCeiling.sol";
import "./BonusFinalizeAgent.sol";

// This contract has the sole objective of providing a sane concrete instance of the Crowdsale contract.
contract HubiiCrowdsale is Crowdsale {
    uint private constant chunked_multiple = 25 * (10 ** 18);
    uint private constant limit_per_address = 6 * (10 ** 18);
    uint private constant token_initial_supply = 0;
    uint8 private constant token_decimals = 8;
    bool private constant token_mintable = true;
    function HubiiCrowdsale(address _teamMultisig, uint _start, uint _end) Crowdsale(_teamMultisig, _start, _end, 5 * (10 ** 18)) public {
        // Due to lack of macros and lack of floating point support
        // we explain the used literals here.
        // 1/500 is the tokens per wei ratio.
        // 8 is the amount of decimals.
        // 10 ** 8 is the factor used to calculate the amount of decimal tokens per wei ratio.
        PricingStrategy p_strategy = PricingStrategy(new FlatPricing((1/500) * (10 ** 8)));
        CeilingStrategy c_strategy = CeilingStrategy(new FixedCeiling(chunked_multiple, limit_per_address));
        FinalizeAgent f_agent = FinalizeAgent(new BonusFinalizeAgent(3000, _teamMultisig));
        setPricingStrategy(p_strategy);
        setCeilingStrategy(c_strategy);
        // Testing values
        token = new CrowdsaleToken("BurgerKoenig", "BK", token_initial_supply, token_decimals, token_mintable);
        token.setMintAgent(address(f_agent), true);
        token.setReleaseAgent(address(f_agent));
        setFinalizeAgent(f_agent);
    }
}
