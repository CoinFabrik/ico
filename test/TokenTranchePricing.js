const advanceBlock = require('./helpers/advanceBlock');
const advanceToBlock = require('./helpers/advanceToBlock');
const TokenTranchePricing = artifacts.require("../contracts/TokenTranchePricing.sol");

const BigNumber = web3.BigNumber

require('chai')
  .use(require('chai-as-promised'))
  .use(require('chai-bignumber')(BigNumber))
  .should();

contract('TokenTranchePricing', function(accounts) {

  // Tranche scheme (end_amount, start_date, end_date, price)

  it("Should throw during construction", async function() {
    // Unordered ending amounts
    let currentBlock = web3.eth.blockNumber;
    await (TokenTranchePricing.new([2, currentBlock+3, currentBlock+4, 20, 1, currentBlock+3, currentBlock+4, 30])).should.be.rejectedWith('invalid opcode');

    // Unordered ending times
    currentBlock = web3.eth.blockNumber;
    await (TokenTranchePricing.new([2, currentBlock+3, currentBlock+5, 20, 2, currentBlock+3, currentBlock+4, 30])).should.be.rejectedWith('invalid opcode');

    // Already started tranche
    currentBlock = web3.eth.blockNumber;
    await (TokenTranchePricing.new([2, currentBlock-1, currentBlock+3, 20])).should.be.rejectedWith('invalid opcode');
  });

  it("Not totally contained tranches should not throw during construction", async function() {
    // Same time period but different ordered amount limits
    let currentBlock = web3.eth.blockNumber;
    await (TokenTranchePricing.new([1, currentBlock+2, currentBlock+3, 20, 2, currentBlock+2, currentBlock+3, 30])).should.not.be.rejectedWith('invalid opcode');
 
    // Same amount limits but different ordered ending times
    currentBlock = web3.eth.blockNumber;
    await (TokenTranchePricing.new([1, currentBlock+3, currentBlock+4, 20, 1, currentBlock+3, currentBlock+5, 30])).should.not.be.rejectedWith('invalid opcode');
  });

  it("Should return prices correctly", async function() {
    // Prices based on just the amounts
    let currentBlock = web3.eth.blockNumber;
    let tranchePricing = await TokenTranchePricing.new([2, currentBlock+2, currentBlock+10, 20, 4, currentBlock+2, currentBlock+10, 30]);
    await advanceBlock();
    (await tranchePricing.getCurrentPrice(1)).should.be.bignumber.and.equal(20);
    (await tranchePricing.getCurrentPrice(3)).should.be.bignumber.and.equal(30);
  
    // Prices based on time
    currentBlock = web3.eth.blockNumber;
    let secondTrancheBlock =  currentBlock + 5;
    tranchePricing = await TokenTranchePricing.new([5, currentBlock+2, currentBlock+3, 20, 5, currentBlock+4, currentBlock+6, 30]);
    await advanceBlock();
    (await tranchePricing.getCurrentPrice(1)).should.be.bignumber.and.equal(20);
    await advanceToBlock(secondTrancheBlock);
    (await tranchePricing.getCurrentPrice(1)).should.be.bignumber.and.equal(30);
  });

  it("Should throw if not in a tranche", async function() {
    let currentBlock = web3.eth.blockNumber;
    let timeBreachBlock = currentBlock + 5; 
    let tranchePricing = await TokenTranchePricing.new([3, currentBlock+2, currentBlock+4, 20, 10, currentBlock+6, currentBlock+8, 30]);
    await advanceBlock();
    await (tranchePricing.getCurrentPrice(4)).should.be.rejectedWith('invalid opcode');
    await advanceToBlock(timeBreachBlock);
    await (tranchePricing.getCurrentPrice(4)).should.be.rejectedWith('invalid opcode');
  });
});