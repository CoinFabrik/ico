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
    config.startTime = Math.round((new Date(2017, 10, 15)).getTime() / 1000);
    const pre_ico_tranches_start = config.startTime;
    const pre_ico_tranches_end = config.startTime + 60*60*24*3;
    const ico_tranches_start = pre_ico_tranches_end;
    let ico_tranches_end = ico_tranches_start + 60*60*24;

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

    config.endTime = config.tranches[config.tranches.length - 2];
  }
  // Main net configuration
  else {
    //TODO: Set appropriate start to crowdsale. No whitelisting should be necessary.
    config.startTime = Math.round((new Date.UTC(2017, 11, 1)) / 1000);
    config.endTime = Math.round((new Date.UTC(2018, 0, 31)) / 1000);
    //TODO: set appropriate multisig for mainnet deployment
    config.MW_address = "0xA8c39c22822a89bC8EAC413a1FFb93b73fb9c906";

    const pre_ico_tranches_start = Math.round((new Date.UTC(2017, 10, 11, 5, 41)) / 1000);
    const pre_ico_tranches_end = [Math.round((new Date.UTC(2017, 10, 14)) / 1000), 
                                  Math.round((new Date.UTC(2017, 10, 21)) / 1000),
                                  config.startTime];
    const ico_tranches_start = config.startTime;
    const ico_tranches_end = [Math.round((new Date.UTC(2017, 11, 8)) / 1000),
                              Math.round((new Date.UTC(2017, 11, 15)) / 1000),
                              Math.round((new Date.UTC(2017, 11, 22)) / 1000),
                              Math.round((new Date.UTC(2017, 11, 31)) / 1000),
                              Math.round((new Date.UTC(2018, 0, 7)) / 1000),
                              Math.round((new Date.UTC(2018, 0, 20)) / 1000),
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
