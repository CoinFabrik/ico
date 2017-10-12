const BigNumber = web3.BigNumber;
const ReleasableToken = artifacts.require("../contracts/ReleasableToken.sol");

require('chai')
  .use(require('chai-as-promised'))
  .use(require('chai-bignumber')(BigNumber))
  .should();

/**
 * In this test suite all transfers are set to 0 tokens to avoid dealing with 
 * allowances, balances or any other value set by contracts that ReleasableToken
 * extends, but are not set nor directly modified here and should be tested in those 
 * contracts.
 *
 * The sole purpose of doing transfers here is to test that the modifiers 
 * applied to those functions work as expected.
 */


contract('ReleasableToken', function() {
  it("Should not throw during construction", async function() {
    await (ReleasableToken.new()).should.not.rejectedWith('invalid opcode');
  });

  it("Should throw on transfers before release or set transfer agent", async function(){
    let rToken = await ReleasableToken.new({from: web3.eth.accounts[0]});

    //Before release
    await rToken.transferFrom(web3.eth.accounts[0], web3.eth.accounts[1], 0).should.rejectedWith('invalid opcode');
    await rToken.transfer(web3.eth.accounts[1], 0).should.rejectedWith('invalid opcode');

  });

  it("Should throw on set operations by different address from owner", async function(){
    let rToken = await ReleasableToken.new({from: web3.eth.accounts[0]});

    await rToken.setReleaseAgent(web3.eth.accounts[1], {from: web3.eth.accounts[1]}).should.rejectedWith('invalid opcode');
    await rToken.setTransferAgent(web3.eth.accounts[1], true, {from: web3.eth.accounts[1]}).should.rejectedWith('invalid opcode');
  });

  it("Should not throw on set operations by owner", async function(){
    let rToken = await ReleasableToken.new({from: web3.eth.accounts[0]});

    await rToken.setReleaseAgent(web3.eth.accounts[1], {from: web3.eth.accounts[0]}).should.not.rejected;
    await rToken.setTransferAgent(web3.eth.accounts[1], true, {from: web3.eth.accounts[0]}).should.not.rejected;
  });

  it("Should throw on release by not release agent", async function(){
    let rToken = await ReleasableToken.new({from: web3.eth.accounts[0]});

    await rToken.releaseTokenTransfer({from: web3.eth.accounts[1]}).should.rejectedWith('invalid opcode');
    await rToken.transferFrom(web3.eth.accounts[1], web3.eth.accounts[0], 0).should.rejectedWith('invalid opcode');
    await rToken.transfer(web3.eth.accounts[1], 0).should.rejectedWith('invalid opcode');
    await rToken.transferFrom(web3.eth.accounts[0], web3.eth.accounts[1], 0, {from: web3.eth.accounts[1]}).should.rejectedWith('invalid opcode');
    await rToken.transfer(web3.eth.accounts[0], 0, {from: web3.eth.accounts[1]}).should.rejectedWith('invalid opcode');
    await rToken.transferFrom(web3.eth.accounts[0], web3.eth.accounts[1], 0).should.rejectedWith('invalid opcode');
    await rToken.transfer(web3.eth.accounts[0], 0).should.rejectedWith('invalid opcode');
    await rToken.transferFrom(web3.eth.accounts[1], web3.eth.accounts[0], 0, {from: web3.eth.accounts[1]}).should.rejectedWith('invalid opcode');
    await rToken.transfer(web3.eth.accounts[1], 0, {from: web3.eth.accounts[1]}).should.rejectedWith('invalid opcode');
    
  });

  it("Should throw on transfer by not transfer agent", async function(){
    let rToken = await ReleasableToken.new({from: web3.eth.accounts[0]});

    await rToken.setTransferAgent(web3.eth.accounts[1], true).should.not.rejected;
    await rToken.transferFrom(web3.eth.accounts[0], web3.eth.accounts[1], 0).should.rejectedWith('invalid opcode');
    await rToken.transfer(web3.eth.accounts[1], 0).should.rejectedWith('invalid opcode');
    
  });

  it("Should not throw on transfer by transfer agent", async function(){
    let rToken = await ReleasableToken.new({from: web3.eth.accounts[0]});

    await rToken.setTransferAgent(web3.eth.accounts[1], true).should.not.rejected;
    await rToken.transfer(web3.eth.accounts[0], 0, {from: web3.eth.accounts[1]}).should.not.rejected;
    await rToken.transferFrom(web3.eth.accounts[1], web3.eth.accounts[0], 0, {from: web3.eth.accounts[1]}).should.not.rejected;
    
  });

  it("Should not throw on transfer after release", async function(){
    let rToken = await ReleasableToken.new({from: web3.eth.accounts[0]});

    await rToken.setReleaseAgent(web3.eth.accounts[1]).should.not.rejected;
    await rToken.releaseTokenTransfer({from: web3.eth.accounts[1]}).should.not.rejected;
    await rToken.transfer(web3.eth.accounts[0], 0, {from: web3.eth.accounts[1]}).should.not.rejected;
    await rToken.transferFrom(web3.eth.accounts[1], web3.eth.accounts[0], 0, {from: web3.eth.accounts[1]}).should.not.rejected;
    await rToken.transfer(web3.eth.accounts[1], 0, {from: web3.eth.accounts[0]}).should.not.rejected;
    await rToken.transferFrom(web3.eth.accounts[0], web3.eth.accounts[1], 0, {from: web3.eth.accounts[0]}).should.not.rejected;
    
  });

  it("Should throw on set operations after release", async function(){
    let rToken = await ReleasableToken.new({from: web3.eth.accounts[0]});

    await rToken.setReleaseAgent(web3.eth.accounts[1]).should.not.rejected;
    await rToken.releaseTokenTransfer({from: web3.eth.accounts[1]}).should.not.rejected;
    await rToken.setReleaseAgent(web3.eth.accounts[1]).should.rejectedWith('invalid opcode');
    await rToken.setReleaseAgent(web3.eth.accounts[0]).should.rejectedWith('invalid opcode');
    await rToken.setTransferAgent(web3.eth.accounts[0], true).should.rejectedWith('invalid opcode');
    await rToken.setTransferAgent(web3.eth.accounts[1], true).should.rejectedWith('invalid opcode');

    
  });
});