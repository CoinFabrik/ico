function config_f(web3, network) {
  const config = {};
  const BigNumber = web3.BigNumber;

  config.milieurs_per_eth = new BigNumber(835.16).times(1000);
  
  const ether = (new BigNumber(10)).toPower(18);
  const eur_per_fulltokens = [new BigNumber(1.66666666667), new BigNumber(1.25), new BigNumber(1)];
  const tranches_quantity = eur_per_fulltokens.length;
  const tokens_per_eur = eur_per_fulltokens.map(function(price) {
    return ether.dividedToIntegerBy(price);
  });

  let amounts = [new BigNumber(150000000), new BigNumber(300000000), new BigNumber(340000000)];
  amounts = amounts.map(function(amount) {
    return amount.times(ether);
  });

  config.tranches = [];

  config.MW_address = "0x878d7ed5C194349F37b18688964E8db1EB0fcCa1";

  const half_hour = 60*30;

  const actual_timestamp = web3.eth.getBlock("latest").timestamp;

  config.startTime = (new Date(Date.UTC(2018,3,19))).getTime()/1000;
  config.endTime = (new Date(Date.UTC(2018,7,29))).getTime()/1000;

  const ico_tranches_start = actual_timestamp + half_hour;
  const ico_tranches_end = config.endTime;

  for (let i = 0; i < tranches_quantity; i++) {
    config.tranches.push(amounts[i]);
    config.tranches.push(ico_tranches_start);
    config.tranches.push(ico_tranches_end);
    config.tranches.push(tokens_per_eur[i]);
  }

  return config;
}

module.exports = config_f;