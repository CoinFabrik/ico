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
    uint private constant hubii_minimum_funding = 5; // in ethers
    uint private constant token_initial_supply = 0;
    uint8 private constant token_decimals = 15;
    bool private constant token_mintable = true;
    string private constant token_name = "Hubiits";
    string private constant token_symbol = "HUBI";
    uint private constant token_inWei = 10 ** 15;
    function HubiiCrowdsale(address _teamMultisig, uint _start, uint _end) Crowdsale(_teamMultisig, _start, _end, hubii_minimum_funding.mul(10 ** 18)) public {
        // Due to lack of macros and lack of floating point support
        // we explain the used literals here.
        // Do take care when setting though. The solidity compiler may not have any checks on the boundaries of literals.
        // 1/500 is the tokens per wei ratio.
        // 8 is the amount of decimals.
        // 10 ** 8 is the factor used to calculate the amount of decimal tokens per wei ratio.
        
        PricingStrategy p_strategy = new FlatPricing(token_inWei);
        CeilingStrategy c_strategy = new FixedCeiling(chunked_multiple, limit_per_address);
        FinalizeAgent f_agent = new BonusFinalizeAgent(this, 3000, _teamMultisig); 
        setPricingStrategy(p_strategy);
        setCeilingStrategy(c_strategy);
        // Testing values
        token = new CrowdsaleToken(token_name, token_symbol, token_initial_supply, token_decimals, _teamMultisig, token_mintable);
        token.setMintAgent(address(this), true);
        token.setMintAgent(address(f_agent), true);
        token.setReleaseAgent(address(f_agent));
        setFinalizeAgent(f_agent);
    }
}