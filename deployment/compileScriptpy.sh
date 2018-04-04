mkdir -p build
cd ../contracts
solc19 -o ../deployment/build --abi --bin --overwrite --optimize --optimize-runs 0 Crowdsale.sol
cd ../deployment