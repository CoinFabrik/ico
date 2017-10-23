function config_f(web3) {
  const config = {};
  config.tests = {};

  const BigNumber = web3.BigNumber;

  // 9/8/2017 20:56 UTC block number: 4,137,656
  // 17/8/2017 ~0:00 UTC block number offset: 28,239 at 21.8 seconds per block on average
  // 19/8/2017 17:58 UTC block number: 4,178,454
  // 24/8/2017 ~15:00 UTC block number offset: 19,867 at 21 seconds per block on average
  // 21/8/2017 19:12 UTC block number: 4,187,037
  // 24/8/2017 ~15:00 UTC block number offset: 11,263  at 21.67 seconds per block on average
  config.startBlock = 4187037 + 11263;
  // We give two week's worth of blocks for the crowdsale to run its course: 55,819 at 21.67 seconds per block on average
  config.endBlock = config.startBlock + 55819;
  config.startTime = 1;
  config.endTime = 1000000000000;
  config.MW_address = "0xe190E5cb7E5E5BE452Dc3C3B34033C7213D3B4df";

  // This is our multisig wallet in mainnet that we use for testing.
  config.fundingCap = web3.toWei("180000");
  config.multisig_owners = ["0xf19258256b06324c7516b00bf5c76af001ee1e95"];
   


  const ether_in_eur = new BigNumber(287.31);
  const pre_ico_tranches_quantity = 3;
  const tranches_quantity = 11;

  config.pre_ico_tranches_start = Math.round(Date.now()/1000);
  config.pre_ico_tranches_end = Math.round(Date.now()/1000);
  config.ico_tranches_start = Math.round(Date.now()/1000);
  config.ico_tranches_end = Math.round(Date.now()/1000);

  const eur_per_fulltokens = [new BigNumber(0.07), new BigNumber(0.08), new BigNumber(0.09), new BigNumber(0.10), new BigNumber(0.11), new BigNumber(0.12), new BigNumber(0.13), new BigNumber(0.14), new BigNumber(0.15), new BigNumber(0.16), new BigNumber(0.17)];

  const tokens_per_wei = eur_per_fulltokens.map(function(price) {
    return ether_in_eur.dividedToIntegerBy(price);    
  });
  
  const amounts = [new BigNumber(60000), new BigNumber(120000), new BigNumber(200000)];

  for (let i = pre_ico_tranches_quantity; i < tranches_quantity; i++) {
    amounts.push(amounts[i-1].add(50*(10**6)));
  }
  amounts.forEach(function(amount) {
    return amount.times(10**18);
  });

  config.tranches = [];

  for (let i = 0; i < pre_ico_tranches_quantity; i++) {
    config.tranches.push(amounts[i]);
    config.tranches.push(config.pre_ico_tranches_start);
    config.tranches.push(config.pre_ico_tranches_end);
    config.tranches.push(tokens_per_wei[i]);
  }

  for (let i = pre_ico_tranches_quantity; i < tranches_quantity; i++) {
    config.tranches.push(amounts[i]);
    config.tranches.push(config.ico_tranches_start);
    config.tranches.push(config.ico_tranches_end);
    config.tranches.push(tokens_per_wei[i]);    
  }

  //Values for testing purposes only

  config.tests.startBlock = web3.eth.blockNumber + 10;
  config.tests.endBlock = config.tests.startBlock + 70;
  
  config.tests.multisig_owners = ["0x8ffc991fc4c4fc53329ad296c1afe41470cffbb3"];

  config.tests.pre_ico_tranches_quantity = 1;
  config.tests.tranches_quantity = 2;

  config.tests.pre_ico_tranches_start = web3.eth.getBlock("latest").timestamp+(3*60);

  config.tests.pre_ico_tranches_end = config.tests.pre_ico_tranches_start+(3*60);
  config.tests.ico_tranches_start = config.tests.pre_ico_tranches_start+(5*60);
  config.tests.ico_tranches_end = config.tests.pre_ico_tranches_start+(60*60);

  config.tests.startTime = config.tests.ico_tranches_start;
  config.tests.endTime = config.tests.ico_tranches_end;

  config.tests.tranches = [];

  for (let i = 0; i < config.tests.pre_ico_tranches_quantity; i++) {
    config.tests.tranches.push(amounts[i]);
    config.tests.tranches.push(config.tests.pre_ico_tranches_start);
    config.tests.tranches.push(config.tests.pre_ico_tranches_end);
    config.tests.tranches.push(tokens_per_wei[i]);
  }

  for (let i = config.tests.pre_ico_tranches_quantity; i < config.tests.tranches_quantity; i++) {
    config.tests.tranches.push(amounts[i]);
    config.tests.tranches.push(config.tests.ico_tranches_start);
    config.tests.tranches.push(config.tests.ico_tranches_end);
    config.tests.tranches.push(tokens_per_wei[i]);    
  }


  return config;
}

module.exports = config_f;
