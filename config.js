function config_f(web3, network) {
  const config = {};
  const BigNumber = web3.BigNumber;

  const tokens_per_wei = [new BigNumber(410), new BigNumber(390), new BigNumber(370), new BigNumber(350),
                          new BigNumber(340), new BigNumber(330), new BigNumber(320), new BigNumber(310),
                          new BigNumber(300), new BigNumber(290), new BigNumber(280)];
  const tranches_quantity = tokens_per_wei.length;
  
  const amounts = [new BigNumber("3500000"), new BigNumber("7000000"), new BigNumber("10500000")];
  const pre_ico_tranches_quantity = amounts.length;
  const ico_tranches_quantity = tranches_quantity - pre_ico_tranches_quantity;

  const amounts = [new BigNumber(60000000), new BigNumber(120000000), new BigNumber(200000000)];
  const pre_ico_tranches_quantity = amounts.length;
  for (let i = pre_ico_tranches_quantity; i < tranches_quantity; i++) {
    amounts.push(amounts[i - 1].add(525*(10**4)));
  }
  amounts.forEach(function(amount) {
    return amount.times((new BigNumber(10)).toPower(18));
  });

  config.tranches = [];

  //Values for testing purposes only
  if (network != "liveNet") {
    config.multisig_owners = ["0xf19258256b06324c7516b00bf5c76af001ee1e95"];
    config.startTime = Math.round((new Date(2017, 10, 28)).getTime() / 1000);
    const pre_ico_tranches_start = config.startTime - 60*60*24*3;
    const pre_ico_tranches_end = config.startTime;
    const ico_tranches_start = config.startTime;
    let ico_tranches_end = config.startTime + 60*60*24;

    for (let i = 0; i < pre_ico_tranches_quantity; i++) {
      config.tranches.push(amounts[i]);
      config.tranches.push(pre_ico_tranches_start);
      config.tranches.push(pre_ico_tranches_end);
      config.tranches.push(tokens_per_wei[i]);
    }

    for (let i = pre_ico_tranches_quantity; i < tranches_quantity; i++) {
      config.tranches.push(amounts[i]);
      config.tranches.push(ico_tranches_start);
      config.tranches.push(ico_tranches_end);
      config.tranches.push(tokens_per_wei[i]);
      ico_tranches_end += 60*60*24; 
    }

    config.endTime = ico_tranches_end;
  }
  // Main net configuration
  else {
    //TODO: Set appropriate start to crowdsale. No whitelisting should be necessary.
    config.startTime = Math.round((new Date(2017, 12, 1)).getTime() / 1000);
    config.endTime = Math.round((new Date(2018, 1, 31)).getTime() / 1000);
    //TODO: set appropriate multisig for mainnet deployment
    config.MW_address = "0xe190E5cb7E5E5BE452Dc3C3B34033C7213D3B4df";

    const pre_ico_tranches_start = Math.round((new Date(2017, 11, 7)).getTime() / 1000);
    const pre_ico_tranches_end = [Math.round((new Date(2017, 11, 14)).getTime() / 1000), 
                                  Math.round((new Date(2017, 11, 21)).getTime() / 1000),
                                  config.startTime];
    const ico_tranches_start = config.startTime;
    const ico_tranches_end = [Math.round((new Date(2017, 12, 8)).getTime() / 1000),
                              Math.round((new Date(2017, 12, 15)).getTime() / 1000),
                              Math.round((new Date(2017, 12, 22)).getTime() / 1000),
                              Math.round((new Date(2017, 12, 31)).getTime() / 1000),
                              Math.round((new Date(2018, 1, 7)).getTime() / 1000),
                              Math.round((new Date(2018, 1, 20)).getTime() / 1000),
                              config.endTime];
    const tranches_end = pre_ico_tranches_end.concat(ico_tranches_end);

    for (let i = 0; i < tranches_quantity; i++) {
      config.tranches.push(amounts[i]);
      config.tranches.push(i < pre_ico_tranches_quantity ? pre_ico_tranches_start : ico_tranches_start);
      config.tranches.push(tranches_end[i]);
      config.tranches.push(tokens_per_wei[i]);
    }
  }

  return config;
}

module.exports = config_f;
