const advanceBlock = require('./helpers/advanceBlock');
const advanceToBlock = require('./helpers/advanceToBlock');
const latestBlockTime = require('./helpers/latestBlockTime');
const TokenTranchePricing = artifacts.require("../contracts/TokenTranchePricing.sol");
const durations = require('./helpers/durations');
const minutes = durations.minutes;
const hours = durations.hours;
const increaseTimes = require('./helpers/increaseTime');
const increaseTime = increaseTimes.increaseTime;
const increaseTimeTo = increaseTimes.increaseTimeTo;

const BigNumber = web3.BigNumber;

require('chai')
  .use(require('chai-as-promised'))
  .use(require('chai-bignumber')(BigNumber))
  .should();

contract('TokenTranchePricing', function(accounts) {

  // Tranche scheme (end_amount, start_date, end_date, price)

  it("Should throw during construction", async function() {
    // Unordered ending amounts
    await increaseTime(minutes(1));
    let current_time = latestBlockTime();
    await (TokenTranchePricing.new([2, current_time+hours(1)+minutes(3), current_time+hours(2)+minutes(4), 20, 1, current_time+hours(1)+minutes(3), current_time+hours(2)+minutes(4), 30])).should.be.rejectedWith('invalid opcode');

    // Unordered ending times
    await increaseTime(minutes(1));
    current_time = latestBlockTime();
    await (TokenTranchePricing.new([2, current_time+hours(1)+minutes(3), current_time+hours(2)+minutes(5), 20, 2, current_time+hours(1)+minutes(3), current_time+hours(2)+minutes(4), 30])).should.be.rejectedWith('invalid opcode');

    // Already started tranche
    await increaseTime(minutes(1));
    current_time = latestBlockTime();
    await (TokenTranchePricing.new([2, current_time-minutes(1), current_time+hours(1)+minutes(3), 20])).should.be.rejectedWith('invalid opcode');

    // Less than an hour between start and end
    await increaseTime(minutes(1));
    current_time = latestBlockTime();
    await (TokenTranchePricing.new([2, current_time+hours(1)+minutes(1), current_time+hours(1)+minutes(3), 20])).should.be.rejectedWith('invalid opcode');
  });

  it("Non-equally tranches should not throw during construction", async function() {
    // Same time period but different ordered amount limits
    await increaseTime(minutes(1));    
    let current_time = latestBlockTime();
    await (TokenTranchePricing.new([1, current_time+hours(1)+minutes(2), current_time+hours(2)+minutes(3), 20, 2, current_time+hours(1)+minutes(2), current_time+hours(2)+minutes(3), 30])).should.not.be.rejected;
 
    // Same amount limits but different ordered ending times
    await increaseTime(minutes(1));
    current_time = latestBlockTime();
    await (TokenTranchePricing.new([5, current_time+hours(1)+minutes(3), current_time+hours(2)+minutes(4), 20, 5, current_time+hours(1)+minutes(3), current_time+hours(2)+minutes(5), 30])).should.not.be.rejected;
  });

  it("Should return prices correctly", async function() {
    // Prices based on just the amounts
    let current_time = latestBlockTime();
    let tranchePricing = await TokenTranchePricing.new([2, current_time+hours(1)+minutes(2), current_time+hours(2)+minutes(10), 20, 4, current_time+hours(1)+minutes(2), current_time+hours(2)+minutes(10), 30]);
    // await advanceBlock();
    await increaseTimeTo(current_time+hours(1)+minutes(3));
    (await tranchePricing.getCurrentPrice(1)).should.be.bignumber.and.equal(20);
    (await tranchePricing.getCurrentPrice(3)).should.be.bignumber.and.equal(30);
  
    // Prices based on time
    current_time = latestBlockTime();
    let firstTrancheStartTime = current_time+hours(1)+minutes(10);
    let firstTrancheEndTime = firstTrancheStartTime+hours(1)+minutes(10);
    let secondTrancheStartTime =  firstTrancheEndTime+hours(1)+minutes(10);
    let secondTrancheEndTime = secondTrancheStartTime+hours(1)+minutes(10);
    tranchePricing = await TokenTranchePricing.new([5, firstTrancheStartTime, firstTrancheEndTime, 20, 5, secondTrancheStartTime, secondTrancheEndTime, 30]);
    await increaseTimeTo(firstTrancheStartTime);
    (await tranchePricing.getCurrentPrice(1)).should.be.bignumber.and.equal(20);
    await increaseTimeTo(secondTrancheStartTime);
    (await tranchePricing.getCurrentPrice(1)).should.be.bignumber.and.equal(30);
  });

  it("Should throw if not in a tranche", async function() {

    let current_time = latestBlockTime();
    let firstTrancheStartTime = current_time+hours(1)+minutes(10);
    let firstTrancheEndTime = firstTrancheStartTime+hours(1)+minutes(10);
    let betweenTranchesTime = firstTrancheEndTime+hours(1);
    let secondTrancheStartTime =  betweenTranchesTime+hours(1)+minutes(10);
    let secondTrancheEndTime = secondTrancheStartTime+hours(1)+minutes(10);
    let lastTranchePastTime = secondTrancheEndTime+hours(1);
    let tranchePricing = await TokenTranchePricing.new([5, firstTrancheStartTime, firstTrancheEndTime, 20, 5, secondTrancheStartTime, secondTrancheEndTime, 30]);
    await increaseTimeTo(betweenTranchesTime);
    await (tranchePricing.getCurrentPrice(4)).should.be.rejectedWith('invalid opcode');
    await increaseTimeTo(lastTranchePastTime);
    await (tranchePricing.getCurrentPrice(4)).should.be.rejectedWith('invalid opcode');
  });
});