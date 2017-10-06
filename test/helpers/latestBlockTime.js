module.exports = function latestBlockTime() {
  return web3.eth.getBlock("latest").timestamp;
}