#!/bin/sh
cd contracts
solc --abi --bin --overwrite --optimize --optimize-runs 0 -o ../compilation Crowdsale.sol
cp -f ../compilation/Crowdsale.bin ../deployment/build
cp -f ../compilation/Crowdsale.abi ../deployment/build
cp -f ../compilation/CrowdsaleToken.abi ../deployment/build
