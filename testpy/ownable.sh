#!/bin/sh

mkdir -p build
cd build
mkdir -p ownable
cd ../../contracts
solc -o ../testpy/build/ownable --abi --bin --overwrite --optimize --optimize-runs 0 Ownable.sol
cd ../testpy