const advanceBlock = require('./advanceBlock');

module.exports = async function advanceToBlock(number) {
  while (web3.eth.blockNumber < number) {
    await advanceBlock();
  }
}