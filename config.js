function config_f(web3, network) {
  const config = {};
  const BigNumber = web3.BigNumber;

  const ether_in_eur = new BigNumber(287.31);
  const eur_per_fulltokens = [new BigNumber(0.07), new BigNumber(0.08), new BigNumber(0.09), new BigNumber(0.10),
                              new BigNumber(0.11), new BigNumber(0.12), new BigNumber(0.13), new BigNumber(0.14),
                              new BigNumber(0.15), new BigNumber(0.16), new BigNumber(0.17)];
  const tranches_quantity = eur_per_fulltokens.length;
  const tokens_per_wei = eur_per_fulltokens.map(function(price) {
    return ether_in_eur.dividedToIntegerBy(price);
  });

  const amounts = [new BigNumber(60000000), new BigNumber(120000000), new BigNumber(200000000)];
  const pre_ico_tranches_quantity = amounts.length;
  for (let i = pre_ico_tranches_quantity; i < tranches_quantity; i++) {
    amounts.push(amounts[i - 1].add(50*(10**6)));
  }
  amounts.forEach(function(amount) {
    return amount.times(10**18);
  });

  config.tranches = [];

  if (network != "liveNet") {
    //TODO: configure dates
    config.startTime = 1;
    config.endTime = 1000000000000;
    config.MW_address = "0x878d7ed5C194349F37b18688964E8db1EB0fcCa1";

    //TODO: configure tranche dates
    const pre_ico_tranches_start = Math.round(Date.now()/1000);
    const pre_ico_tranches_end = Math.round(Date.now()/1000);
    const ico_tranches_start = Math.round(Date.now()/1000);
    const ico_tranches_end = Math.round(Date.now()/1000);


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
    }
  }
  //Values for testing purposes only
  else {
    config.multisig_owners = ["0x8ffc991fc4c4fc53329ad296c1afe41470cffbb3"];

    const half_year = 60*60*24*182;
    const half_day = 60*60*12;
    const pre_ico_tranches_start = web3.eth.getBlock("latest").timestamp + half_day;
    const pre_ico_tranches_end = pre_ico_tranches_start + half_year;
    const ico_tranches_start = pre_ico_tranches_start;
    const ico_tranches_end = pre_ico_tranches_start + half_year;

    config.startTime = ico_tranches_start;
    config.endTime = ico_tranches_end;

    for (let i = 0; i < config.pre_ico_tranches_quantity; i++) {
      config.tranches.push(amounts[i]);
      config.tranches.push(pre_ico_tranches_start);
      config.tranches.push(pre_ico_tranches_end);
      config.tranches.push(tokens_per_wei[i]);
    }

    for (let i = config.pre_ico_tranches_quantity; i < config.tranches_quantity; i++) {
      config.tranches.push(amounts[i]);
      config.tranches.push(ico_tranches_start);
      config.tranches.push(ico_tranches_end);
      config.tranches.push(tokens_per_wei[i]);
    }
  }

  return config;
}

module.exports = config_f;
