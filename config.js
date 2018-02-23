function config_f(web3, network) {
  const config = {};
  const BigNumber = web3.BigNumber;

  config.milieurs_per_eth = new BigNumber(647.65).times(1000);
  const thousand = new BigNumber(1000);
  const ether = (new BigNumber(10)).toPower(18);
  const eur_per_fulltokens = [new BigNumber(0.10), new BigNumber(0.12),
                              new BigNumber(0.14), new BigNumber(0.17),
                              new BigNumber(0.20), new BigNumber(0.25)];
  const tranches_quantity = eur_per_fulltokens.length;
  const tokens_per_eur = eur_per_fulltokens.map(function(price) {
    return ether.dividedToIntegerBy(price);
  });

  let amounts = [new BigNumber(350000000)];
  const pre_ico_tranches_quantity = amounts.length;
  for (let i = pre_ico_tranches_quantity; i < tranches_quantity; i++) {
    amounts.push(amounts[i - 1].add(50*(10**6)));
  }
  amounts = amounts.map(function(amount) {
    return amount.times(ether);
  });

  config.tranches = [];

  //Values for testing purposes only
  if (network != "liveNet") {
    config.multisig_owners = ["0x8ffc991fc4c4fc53329ad296c1afe41470cffbb3"];

    const half_year = 60*60*24*182;
    const half_day = 60*60*12;
    const one_minute = 60;
    const three_minutes = 60*3;
    const ten_minutes = 60*10;

    const pre_ico_tranches_start = web3.eth.getBlock("latest").timestamp + one_minute;
    const pre_ico_tranches_end = pre_ico_tranches_start + ten_minutes;
    const ico_tranches_start = pre_ico_tranches_end;
    const ico_tranches_end = pre_ico_tranches_start + half_year;

    config.startTime = ico_tranches_start;
    config.endTime = ico_tranches_end;

    for (let i = 0; i < pre_ico_tranches_quantity; i++) {
      config.tranches.push(amounts[i]);
      config.tranches.push(pre_ico_tranches_start);
      config.tranches.push(pre_ico_tranches_end);
      config.tranches.push(tokens_per_eur[i]);
    }

    for (let i = pre_ico_tranches_quantity; i < tranches_quantity; i++) {
      config.tranches.push(amounts[i]);
      config.tranches.push(ico_tranches_start);
      config.tranches.push(ico_tranches_end);
      config.tranches.push(tokens_per_eur[i]);
    }
  }
  // Main net configuration
  else {
    config.MW_address = "0x878d7ed5C194349F37b18688964E8db1EB0fcCa1";

    const half_year = 182*24*60*60;
    const twelve_hours = 12*60*60;
    const one_hour = 1*60*60;

    const actual_timestamp = web3.eth.getBlock("latest").timestamp;

    config.startTime = actual_timestamp + one_hour;
    config.endTime = config.startTime + half_year;

    const ico_tranches_start = config.startTime;
    const ico_tranches_end = config.endTime;

    for (let i = 0; i < tranches_quantity; i++) {
      config.tranches.push(amounts[i]);
      config.tranches.push(ico_tranches_start);
      config.tranches.push(ico_tranches_end);
      config.tranches.push(tokens_per_eur[i]);
    }
  }

  return config;
}

module.exports = config_f;
