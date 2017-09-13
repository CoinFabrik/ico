function config_f(web3) {
  const config = {};
  config.tests = {};

  // 9/8/2017 20:56 UTC block number: 4,137,656
  // 17/8/2017 ~0:00 UTC block number offset: 28,239 at 21.8 seconds per block on average
  // 19/8/2017 17:58 UTC block number: 4,178,454
  // 24/8/2017 ~15:00 UTC block number offset: 19,867 at 21 seconds per block on average
  // 21/8/2017 19:12 UTC block number: 4,187,037
  // 24/8/2017 ~15:00 UTC block number offset: 11,263  at 21.67 seconds per block on average
  config.startBlock = 4187037 + 11263;
  // We give two week's worth of blocks for the crowdsale to run its course: 55,819 at 21.67 seconds per block on average
  config.endBlock = config.startBlock + 55819;
  config.MW_address = "0xe190E5cb7E5E5BE452Dc3C3B34033C7213D3B4df";
  // This is our multisig wallet in mainnet that we use for testing.
  config.fundingCap = web3.toWei("180000");
  config.multisig_owners = ["0xf19258256b06324c7516b00bf5c76af001ee1e95"];


  config.tests.startBlock = web3.eth.getBlock("latest").number + 10;
  config.tests.endBlock = config.tests.startBlock + 70;
  config.tests.multisig_owners = ["0x8ffc991fc4c4fc53329ad296c1afe41470cffbb3"];
  return config;
}

module.exports = config_f;
