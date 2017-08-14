pragma solidity ^0.4.13;

import "./Crowdsale.sol";
import "./CrowdsaleToken.sol";
import "./FlatPricing.sol";
import "./FixedCeiling.sol";
import "./BonusFinalizeAgent.sol";

// This contract has the sole objective of providing a sane concrete instance of the Crowdsale contract.
contract HubiiCrowdsale is Crowdsale {
    uint private constant chunked_multiple = 25 * (10 ** 18); // in wei
    uint private constant limit_per_address = 6 * (10 ** 18); // in wei
    uint private constant hubii_minimum_funding = 5 * (10 ** 18); // in wei
    uint private constant token_initial_supply = 0;
    // uint8 private constant token_decimals = 15;
    // bool private constant token_mintable = true;
    // string private constant token_name = "Hubiits";
    // string private constant token_symbol = "HUBI";
    uint private constant token_in_wei = 10 ** 15;
    // The fraction of 10,000 out of the total target tokens that is used to mint bonus tokens. These are allocated to the team's multisig wallet.
    uint private constant bonus_base_points = 3000;
    function HubiiCrowdsale(address _teamMultisig, uint _start, uint _end) Crowdsale(_teamMultisig, _start, _end, hubii_minimum_funding) public {
        preparing = true;
        PricingStrategy p_strategy = new FlatPricing(token_in_wei);
        CeilingStrategy c_strategy = new FixedCeiling(chunked_multiple, limit_per_address);
        setPricingStrategy(p_strategy);
        setCeilingStrategy(c_strategy);
        // Testing values
        // token = new CrowdsaleToken(token_name, token_symbol, token_initial_supply, token_decimals, _teamMultisig, token_mintable);
    }

    function finishInitialization(CrowdsaleToken token_addr) public inState(State.Preparing) onlyOwner {
        token = token_addr;
        FinalizeAgent f_agent = new BonusFinalizeAgent(this, bonus_base_points, multisigWallet); 
        token.setMintAgent(address(this), true);
        token.setMintAgent(address(f_agent), true);
        token.setReleaseAgent(address(f_agent));
        setFinalizeAgent(f_agent);
        preparing = false;
    }
}