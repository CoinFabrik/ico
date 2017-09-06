const config = {};

// config.nodeIpPort = "http://127.0.0.1:20487";
config.ipc_file = process.env.HOME + "/.ethereum/geth.ipc";
config.crowdsale = {
  address: "0xb9aac097f4dadcd6f06761eb470346415ef28d5a"
};
config.ceiling_strategy = {
  address: "0xd80df9c12982e1746c4f3dfc75e267d404527ffc"
};

module.exports = config;