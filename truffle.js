module.exports = {
  networks: {
    development: {
      host: "192.168.0.149",
      port: 8545,
      network_id: "*", // Match any network id
      from: "0x4cdabc27b48893058aa1675683af3485e4409eff",
      gas: 4612388
    }
  }
};
