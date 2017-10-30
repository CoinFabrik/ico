module.exports = {
  networks: {
    liveNet: {
        host: "localhost",
        port: 8545,
        network_id: "1",
        from: "0x54d9249c776c56520a62faecb87a00e105e8c9dc",
        gas: 100000,
        gasPrice: 5000000000
    },
    ropsten: {
      host: "localhost",
      port: 8545,
      network_id: "3", // Match any network id
      // from: "0x485de458fbcac6a7d35227842d652641384cb333", //// Defaults to the first available account provided by your Ethereum client.
      gas: 4612388,
      gasPrice: 20000000000
    },
    testrpc: {
      host: "localhost",
      port: 20487,
      network_id: "*",
      from: "0x52f96788017f9185a67a86c3a270d28e0fccd751", // Defaults to the first available account provided by your Ethereum client.
      gas: 4612388,
      gasPrice: 20000000000
    },
    privateTestnet:{
      host: "localhost",
      port: 7999,
      network_id: 666,
      //from: default,
      gas: 6500000,
      gasPrice: 20000000000 
    }
  },
  gasPrice: 20000000000,
  solc: {
    optimizer: {
      enabled: true,
      runs: 0
    }
  }
};
