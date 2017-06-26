const RandomBytes = require('random-bytes');

const SafeMath = artifacts.require('./SafeMath.sol');
const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const FlatPricing = artifacts.require('./FlatPricing.sol');
const BonusFinalizeAgent = artifacts.require('./BonusFinalizeAgent.sol');
const CrowdsaleToken = artifacts.require('./CrowdsaleToken.sol');
const DynamicCeiling = artifacts.require('./DynamicCeiling.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');

// TODO: adapt to client needs
const TOKEN_NAME = 'TokenI';
const TOKEN_SYMBOL = 'TI';
const INITIAL_SUPPLY = 1000;
const DECIMALS = 2;
const MINTABLE = true;
const PRICE = 500;
const START_DATE = 1498867200;
const END_DATE = 1500000000;
const MINIMUM_FUNDING_GOAL = 2000;
const BONUS_BASE_POINTS = 300000; // equivalent to 30%
const CURVES = [
    [web3.toWei(1000), 30, 10**12],
    [web3.toWei(21000), 30, 10**12],
    [web3.toWei(61000), 30, 10**12],
];
const NHIDDENCURVES = 7;

const setHiddenCurves = async function(dynamicCeiling, curves, nHiddenCurves) {
    let hashes = [];
    let i = 0;
    for (let c of curves) {
        let salt = await RandomBytes(32);
        let h = await dynamicCeiling.calculateHash(c[0], c[1], c[2], i === curves.length - 1, salt);
        hashes.push(h);
        i += 1;
    }
    for (; i < nHiddenCurves; i += 1) {
        let salt = RandomBytes(32);
        hashes.push(web3.sha3(salt));
    }
    await dynamicCeiling.setHiddenCurves(hashes);
};

module.exports = function(deployer) {
    deployer.deploy(SafeMath);
    deployer.link(SafeMath, FlatPricing);
    deployer.link(SafeMath, BonusFinalizeAgent);
    deployer.link(SafeMath, CrowdsaleToken);
    deployer.link(SafeMath, DynamicCeiling);
    deployer.link(SafeMath, Crowdsale);

    let CT_contract = [ CrowdsaleToken, TOKEN_NAME, TOKEN_SYMBOL, INITIAL_SUPPLY, DECIMALS, MINTABLE ];
    let FP_contract = [ FlatPricing, PRICE ];
    let DC_contract = [ DynamicCeiling ];
    let MW_contract = [ MultiSigWallet, [0x4cdabc27b48893058aa1675683af3485e4409eff], 1 ];
    return deployer.deploy([ CT_contract, FP_contract, DC_contract, MW_contract ]).then(async () => {
        await deployer.deploy(Crowdsale, CrowdsaleToken.address, FlatPricing.address, DynamicCeiling.address, MultiSigWallet.address, START_DATE,  END_DATE,  MINIMUM_FUNDING_GOAL);
    }).then(async () => {
        await deployer.deploy(BonusFinalizeAgent, CrowdsaleToken.address, Crowdsale.address, BONUS_BASE_POINTS, MultiSigWallet.address);
    }).then(async () => {
        let DC_prom = DynamicCeiling.deployed()
        .then(async function(ceilingInstance) {
            console.log('Setting hidden curves in ceiling strategy\'s contract...');
            await setHiddenCurves(ceilingInstance, CURVES, NHIDDENCURVES);
        });

        let CT_prom = CrowdsaleToken.deployed()
        .then(async function(tokenInstance) {
            console.log('Setting Crowdsale as mint agent of CrowdsaleToken...');
            await tokenInstance.setMintAgent(Crowdsale.address, true);
            console.log('Setting BonusFinalizeAgent as mint agent of CrowdsaleToken...');
            await tokenInstance.setMintAgent(BonusFinalizeAgent.address, true);
            console.log('Setting BonusFinalizeAgent as release agent of CrowdsaleToken...');
            await tokenInstance.setReleaseAgent(BonusFinalizeAgent.address);
            console.log('Transfering ownership of CrowdsaleToken to MultiSigWallet...');
            tokenInstance.transferOwnership(MultiSigWallet.address);
        });
        
        let C_prom = Crowdsale.deployed()
        .then(async function(crowdsaleInstance) {
            console.log('Setting BonusFinalizeAgent as finalize agent of Crowdsale...');
            await crowdsaleInstance.setFinalizeAgent(BonusFinalizeAgent.address);
            console.log('Transfering ownership of Crowdsale contract to MultiSigWallet...');
            crowdsaleInstance.transferOwnership(MultiSigWallet.address);
        });
        await Promise.all([ DC_prom, CT_prom, C_prom ]);
    }).catch((error) => {
        console.log(error);
    });

};