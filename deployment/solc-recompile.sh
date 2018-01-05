cd ../contracts
solc --abi --bin --overwrite --optimize --optimize-runs 0 -o ../deployment/build Crowdsale.sol
cd ../deployment

echo -n "module.exports = '" > Crowdsale.bin.js
cat build/Crowdsale.bin >> Crowdsale.bin.js
echo "';" >> Crowdsale.bin.js

echo -n "module.exports = " > Crowdsale.abi.js
cat build/Crowdsale.abi >> Crowdsale.abi.js
echo ";" >> Crowdsale.abi.js

