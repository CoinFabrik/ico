#!/bin/sh

mkdir -p build
cd ../contracts
solc -o ../tests/build/ --abi --bin --overwrite --optimize --optimize-runs 0 Haltable.sol Ownable.sol TokenTranchePricingMock.sol UpgradeableTokenMock.sol UpgradeAgentMock.sol StandardTokenMock.sol MintableTokenMock.sol LostAndFoundTokenMock.sol GenericCrowdsaleMock.sol ReleasableToken.sol
cd ../tests