# ICO Framework

## Requirements

- Python 3
- Web3.py v4.2.1

## Before deployment

This is a set of contracts meant to be used as a baseline for an ICO. As such, there are a few functions missing an implementation in the `Crowdsale` contract. It is strongly recommended to read the [design](Design.md) and the comments for each of the following contracts before deployment: [`Crowdsale`](contracts/Crowdsale.sol) and [`GenericCrowdsale`](contracts/GenericCrowdsale.sol).

## Commands

- `cd deployment`
- `./crowdsale_deployment.py -n mainnet`: Deploys contract to mainnet.
- `./configurate.py`: Sets the configuration of the contracts.