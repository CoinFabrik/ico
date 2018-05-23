# ICO Framework

## Requirements

- Python 3
- Web3.py v4.2.1

## Before deployment

This is a set of contracts meant to be used as a baseline for an ICO. As such, there are a few functions missing an implementation in the `Crowdsale` contract. It is strongly recommended to read the [design](Design.md) and the comments for each of the following contracts before deployment: [`Crowdsale`](contracts/Crowdsale.sol) and [`GenericCrowdsale`](contracts/GenericCrowdsale.sol).

Before deployment configurate [`networks`](deployment/networks.json) to fit your setup and enter the correct configuration in [`client_config`](deployment/client_config.py) for your deployment. For more information on deployment go to [`Deployment_Instructions`](deployment/Deployment_Instructions.md).

## Commands

- `cd deployment`: Goes to deployment directory.
- `./recompile.sh`: Compiles smart contract.
- `./deploy.py -n mainnet`: Deploys contract to mainnet.
- `./configurate.py (-a <address> or -d <deployment_name>)`: Sets the configuration of the contracts.