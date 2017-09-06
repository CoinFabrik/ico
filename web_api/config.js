const config = {};

// config.nodeIpPort = "http://127.0.0.1:20487";
config.ipc_file = process.env.HOME + "/.ethereum/geth.ipc";
config.crowdsale = {
  address: "0x07bff081b3978d9f69dc5f7232825bbff3b1666c"
};
config.ceiling_strategy = {
  address: "0xd80df9c12982e1746c4f3dfc75e267d404527ffc"
};

module.exports = config;