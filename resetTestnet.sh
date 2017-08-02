cd ../.testnet
rm -rf `ls | grep -v keystore`
geth --datadir ../.testnet init ../testnetGenesis.json
