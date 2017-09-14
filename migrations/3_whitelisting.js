const MultiSigWallet = artifacts.require('./MultiSigWallet.sol');
const Crowdsale = artifacts.require('./Crowdsale.sol');
const config = require('../config.js')(web3);

module.exports = function(deployer, network, accounts) {
  deployer.then(function() {
            
  	const crowdsale = Crowdsale.at(Crowdsale.address);

		crowdsale.setDiscountedInvestor("0x0Bb75bEf057da63a0ae4B25fe9aDaFd35cd92B87", true);
		crowdsale.setDiscountedInvestor("0x300532b6404d0c171d3ffEb23f75e9393C73bE9B", true);
		crowdsale.setDiscountedInvestor("0xB2EdF87618E16E24657253De70b5E896DC2a723B", true);
		crowdsale.setDiscountedInvestor("0x57bc8c559dae440db1bb13ebb478b85c5cd097e7", true);
		crowdsale.setDiscountedInvestor("0xef2b3188a2af51b9beb76d82378998c903fe37ea", true);
		crowdsale.setDiscountedInvestor("0xe3f061d9724f0DaACaADa6438B32E7492F2Bf251", true);
		crowdsale.setDiscountedInvestor("0x68f521a871DDd406A57121bf7246c7574Bc3CB62", true);
		crowdsale.setDiscountedInvestor("0xD741A36BcB0856712673bfff0210147754938525", true);
		crowdsale.setDiscountedInvestor("0xc7075ed6bf05549eD8e0d6b11F58721040Ab4D05", true);
		crowdsale.setDiscountedInvestor("0x12f7c4c8977a5b9addb52b83e23c9d0f3b89be15", true);
		crowdsale.setDiscountedInvestor("0x57311928E2FdA6896e420647bB70bbac451da4A2", true);
		crowdsale.setDiscountedInvestor("0x81A5f5550c14a671cb47db08594bF6549E699D74", true);
		crowdsale.setDiscountedInvestor("0xd6b75eC5C30F809205EDE354F717E0A240966711", true);
		crowdsale.setDiscountedInvestor("0x300532b6404d0c171d3ffeb23f75e9393c73be9b", true);
		crowdsale.setDiscountedInvestor("0xD35184b3fb9B3376e4Af80F41C6AB012A9f81f79", true);
		crowdsale.setDiscountedInvestor("0x4D59fdF4A607C93dB5Ccaa3321AF3b2c75A04b3C", true);
		
		// crowdsale.setDiscountedInvestor("Kapperallee43b", true);
			
		crowdsale.setDiscountedInvestor("0x9131dEBBEf705099c19FD14Fa3C04c28aFCeBe47", true);
		crowdsale.setDiscountedInvestor("0xA03C0503c5fBBA0A3a90852bA4cCa4f16C767E8f", true);
		crowdsale.setDiscountedInvestor("0xaF4505a27A67a4AeaA20d8407B36F3af2401c98C", true);
		crowdsale.setDiscountedInvestor("0x9ff8E8E819226B3A4e95a8Bc2ef787A8eb236463", true);
		crowdsale.setDiscountedInvestor("0x98B841eA365CF9AF0e85e57e9F4e26E3a1D9964C", true);
		crowdsale.setDiscountedInvestor("0x01873Be3C68686115C36D694eeBA1780bDA810f6", true);
		crowdsale.setDiscountedInvestor("0xcDC95322054561DdE9B80c2E5A22f8E09BCB80e7", true);
		crowdsale.setDiscountedInvestor("0xcDC95322054561DdE9B80c2E5A22f8E09BCB80e7", true);
		crowdsale.setDiscountedInvestor("0x7927551AeA21d146C065257E06E677A52bA29dE2", true);
		crowdsale.setDiscountedInvestor("0x333c6138925E16C44DB2C6106029b1A4A1FF6653", true);
		crowdsale.setDiscountedInvestor("0xf73619d94b364e6377a386E7893B002cC66C8959", true);
		crowdsale.setDiscountedInvestor("0x7857d131C2A8e8F98E48451Dc989134Eac0C500d", true);
		crowdsale.setDiscountedInvestor("0x945D0f44ADd439645323Ee6dAc2b64ae1c0C30F4", true);
		crowdsale.setDiscountedInvestor("0x1e1D15E2D670c63B9846789c38c28eac68755177", true);
		crowdsale.setDiscountedInvestor("0x526714396E137b4Abb363539178C9C5E3a6c94fe", true);
		crowdsale.setDiscountedInvestor("0xaF876D43a7651B0afC4CFb46dF1EBF1361Df2537", true);
		crowdsale.setDiscountedInvestor("0x5F4fB8cba68Bc18c3720230601Af9FFC854956B9", true);
		crowdsale.setDiscountedInvestor("0x16c95bfF3b8c65411D1c790407FaF33Db5A17649", true);
		crowdsale.setDiscountedInvestor("0x80Fa3656cD2A3602896e492d6DbB3eac9A68BAcF", true);
	});
};