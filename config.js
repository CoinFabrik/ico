function config_f(web3) {
  const config = {};
  config.tests = {};

  // 13/9/2017 17:32 UTC block number: 4,270,244
  // 14/9/2017 ~21:00 UTC block number offset: 3,840 at 25.5 seconds per block on average
  config.startBlock = 4270244 + 3840;
  // We give 46 days worth of blocks for the crowdsale to run its course: 155,858 at 25.5 seconds per block on average
  config.endBlock = config.startBlock + 155858;
  config.MW_address = "0xe190E5cb7E5E5BE452Dc3C3B34033C7213D3B4df";
  // This is our multisig wallet in mainnet that we use for testing.
  config.multisig_owners = ["0xf19258256b06324c7516b00bf5c76af001ee1e95"];


  config.tests.startBlock = web3.eth.blockNumber + 10;
  config.tests.endBlock = config.tests.startBlock + 70;
  config.tests.multisig_owners = ["0x8ffc991fc4c4fc53329ad296c1afe41470cffbb3"];
  return config;
}

module.exports = config_f;
