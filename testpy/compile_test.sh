#!/bin/sh

mkdir -p build
cd build
mkdir -p haltable
mkdir -p ownable
mkdir -p token_tranche_pricing
mkdir -p upgradeable_token
cd ../../contracts
solc -o ../testpy/build/haltable --abi --bin --overwrite --optimize --optimize-runs 0 Haltable.sol
solc -o ../testpy/build/ownable --abi --bin --overwrite --optimize --optimize-runs 0 Ownable.sol
solc -o ../testpy/build/token_tranche_pricing --abi --bin --overwrite --optimize --optimize-runs 0 TokenTranchePricingMock.sol
cd ../testpy