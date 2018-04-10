#!/bin/sh

mkdir -p build
cd build
mkdir -p token_tranche_pricing
cd ../../contracts
solc -o ../testpy/build/token_tranche_pricing --abi --bin --overwrite --optimize --optimize-runs 0 TokenTranchePricingMock.sol
cd ../testpy