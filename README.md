# ICO Sample

## Requirements

- Node.js 8.1.2
- npm 4.6.1
- Truffle 3.2.2
- EthereumJS TestRPC

## Commands

- `truffle compile`
- `truffle migrate`
- `npm run test`: Launches a fresh testrpc instance and runs the testsuite against it.
- `npm run ropsten`: Launches geth to synchronize with the ropsten testnet.
- `npm run ropsten_attach`: Attach to the blockchain node with the geth console.

In Truffle's commands you can specify the network to use with `--network`. Options are: `testrpc` and `ropsten`.
Before using any of them, you should edit [truffle.js](truffle.js) and [package.json](package.json) to point to your own testnet synchronized node.
Instances of testrpc are configured to use port 20487.