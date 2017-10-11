# ICO Framework

## Requirements

- Node.js 8.6.0
- npm 5.3.0
- Truffle 3.4.11
- EthereumJS TestRPC

## Before deployment

This is a set of contracts meant to be used as a baseline for an ICO. As such, there are a few functions missing an implementation in the `Crowdsale` contract. It is strongly recommended to read the [design](Design.md) and the comments for each of the following contracts before deployment: [`Crowdsale`](contracts/Crowdsale.sol) and [`GenericCrowdsale`](contracts/GenericCrowdsale.sol).

## Commands

- `truffle compile`
- `truffle migrate`
- `npm run ropsten`: Launches geth to synchronize with the ropsten testnet.

In Truffle's commands you can specify the network to use with `--network`. Options are: `testrpc` and `ropsten`.
Before using any of them, you should edit [truffle.js](truffle.js) and [package.json](package.json) to point to your own testnet synchronized node.
Instances of testrpc are configured to use port 20487.