#!/bin/sh

mkdir -p build
cd build
mkdir -p haltable
cd ../../contracts
solc -o ../testpy/build/haltable --abi --bin --overwrite --optimize --optimize-runs 0 Haltable.sol
cd ../testpy