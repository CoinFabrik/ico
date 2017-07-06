module.exports = {
  networks: {
    ropsten: {
      host: "localhost",
      port: 8545,
      network_id: "*", // Match any network id
      from: "0x4cdabc27b48893058aa1675683af3485e4409eff",
      gas: 4612388,
      gasPrice: 20000000000
    },
    testrpc: {
      host: "localhost",
      port: 20487,
      network_id: "*",
      from: "0x52f96788017f9185a67a86c3a270d28e0fccd751",
      gas: 4612388,
      gasPrice: 20000000000
    }
  }
};
