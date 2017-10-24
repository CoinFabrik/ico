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
   

  config.tests.startTime = Math.round((new Date(2017, 10, 27)).getTime() / 1000);

  const pre_ico_tranches_start = Math.round((new Date(2017, 10, 24)).getTime() / 1000);
  const pre_ico_tranches_end = config.tests.startTime;
  let ico_tranches_start = config.tests.startTime;
  
  const tokens_per_wei = [new BigNumber(410), new BigNumber(390), new BigNumber(370), new BigNumber(350),
                          new BigNumber(340), new BigNumber(330), new BigNumber(320), new BigNumber(310),
                          new BigNumber(300), new BigNumber(290), new BigNumber(280)];
  
  const amounts = [new BigNumber("3500000"), new BigNumber("7000000"), new BigNumber("10500000")];
  const pre_ico_tranches_quantity = amounts.length;
  const ico_tranches_quantity = tokens_per_wei.length - amounts.length;
  const tranches_quantity = amounts.length + ico_tranches_quantity;
  let ico_tranches_end = config.tests.startTime + 60*60*24*ico_tranches_quantity;

  for (let i = pre_ico_tranches_quantity; i < tranches_quantity; i++) {
    amounts.push(amounts[i - 1].add(525*(10**4)));
  }
  amounts.forEach(function(amount) {
    return amount.times((new BigNumber(10)).toPower(18));
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
    config.tranches.push(ico_tranches_start);
    config.tranches.push(ico_tranches_end);
    config.tranches.push(tokens_per_wei[i]);
    ico_tranches_start += 60*60*24; 
  }
  
  config.tests.endTime = ico_tranches_end;

  //Values for testing purposes only

  // config.tests.startBlock = web3.eth.blockNumber + 10;
  // config.tests.endBlock = config.tests.startBlock + 70;
  
  config.tests.multisig_owners = ["0x8ffc991fc4c4fc53329ad296c1afe41470cffbb3"];

  return config;
}

module.exports = config_f;
