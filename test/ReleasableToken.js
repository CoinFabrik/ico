const BigNumber = web3.BigNumber;
const ReleasableToken = artifacts.require("../contracts/helpers/ReleasableTokenMock.sol");

require('chai')
  .use(require('chai-as-promised'))
  .use(require('chai-bignumber')(BigNumber))
  .should();

function delay_promise(delay) {
	return new Promise(function(resolve, reject) {
  	setTimeout(function() { resolve(); }, delay);
	});
}

contract('ReleasableToken', function() {
  it("Should not throw during construction", async function() {
    await (ReleasableToken.new()).should.not.rejectedWith('invalid opcode');
  });

  it("Should throw on transfers before release or set transfer agent", async function(){
    let rToken = await ReleasableToken.new({from: web3.eth.accounts[0]});

    //Before release
    await rToken.mint(web3.eth.accounts[0], 3).should.not.rejectedWith('invalid opcode');
    await rToken.transferFrom(web3.eth.accounts[0], web3.eth.accounts[1], 0).should.rejectedWith('invalid opcode');
    await rToken.transfer(web3.eth.accounts[1], 1).should.rejectedWith('invalid opcode');
    (await rToken.balanceOf(web3.eth.accounts[0])).should.bignumber.and.equal(3);
    (await rToken.balanceOf(web3.eth.accounts[1])).should.bignumber.and.equal(0);

  });

  it("Should throw on set operations by different address from owner", async function(){
    let rToken = await ReleasableToken.new({from: web3.eth.accounts[0]});

    await rToken.setReleaseAgent(web3.eth.accounts[1], {from: web3.eth.accounts[1]}).should.rejectedWith('invalid opcode');
    await rToken.setTransferAgent(web3.eth.accounts[1], true, {from: web3.eth.accounts[1]}).should.rejectedWith('invalid opcode');
    await rToken.mint(web3.eth.accounts[1], 3).should.not.rejected;
    await rToken.transferFrom(web3.eth.accounts[1], web3.eth.accounts[0], 0).should.rejectedWith('invalid opcode');
    (await rToken.balanceOf(web3.eth.accounts[1])).should.bignumber.and.equal(3);
  });

  it("Should throw on release by not release agent", async function(){
    let rToken = await ReleasableToken.new({from: web3.eth.accounts[0]});
    await rToken.mint(web3.eth.accounts[1], 3).should.not.rejected;
    await rToken.mint(web3.eth.accounts[0], 3).should.not.rejected;

    await rToken.releaseTokenTransfer({from: web3.eth.accounts[1]}).should.rejectedWith('invalid opcode');
    await rToken.transferFrom(web3.eth.accounts[1], web3.eth.accounts[0], 0).should.rejectedWith('invalid opcode');
    await rToken.transfer(web3.eth.accounts[1], 1).should.rejectedWith('invalid opcode');
    await rToken.transferFrom(web3.eth.accounts[0], web3.eth.accounts[1], 0, {from: web3.eth.accounts[1]}).should.rejectedWith('invalid opcode');
    await rToken.transfer(web3.eth.accounts[0], 1, {from: web3.eth.accounts[1]}).should.rejectedWith('invalid opcode');
    await rToken.transferFrom(web3.eth.accounts[0], web3.eth.accounts[1], 0).should.rejectedWith('invalid opcode');
    await rToken.transfer(web3.eth.accounts[0], 1).should.rejectedWith('invalid opcode');
    await rToken.transferFrom(web3.eth.accounts[1], web3.eth.accounts[0], 0, {from: web3.eth.accounts[1]}).should.rejectedWith('invalid opcode');
    await rToken.transfer(web3.eth.accounts[1], 1, {from: web3.eth.accounts[1]}).should.rejectedWith('invalid opcode');
    (await rToken.balanceOf(web3.eth.accounts[0])).should.bignumber.and.equal(3);
    (await rToken.balanceOf(web3.eth.accounts[1])).should.bignumber.and.equal(3);
    
  });

  it("Should throw on transfer by not transfer agent", async function(){
    let rToken = await ReleasableToken.new({from: web3.eth.accounts[0]});
    await rToken.mint(web3.eth.accounts[1], 3).should.not.rejected;
    await rToken.mint(web3.eth.accounts[0], 3).should.not.rejected;

    await rToken.setTransferAgent(web3.eth.accounts[1], true).should.not.rejected;
    await rToken.transferFrom(web3.eth.accounts[0], web3.eth.accounts[1], 0).should.rejectedWith('invalid opcode');
    await rToken.transfer(web3.eth.accounts[1], 1).should.rejectedWith('invalid opcode');
    (await rToken.balanceOf(web3.eth.accounts[0])).should.bignumber.and.equal(3);
    (await rToken.balanceOf(web3.eth.accounts[1])).should.bignumber.and.equal(3);
    
  });

  it("Should not throw on transfer by transfer agent", async function(){
    let rToken = await ReleasableToken.new({from: web3.eth.accounts[0]});
    await rToken.mint(web3.eth.accounts[1], 3).should.not.rejected;
    await rToken.mint(web3.eth.accounts[0], 3).should.not.rejected;

    await rToken.setTransferAgent(web3.eth.accounts[1], true).should.not.rejected;
    await rToken.transfer(web3.eth.accounts[0], 1, {from: web3.eth.accounts[1]}).should.not.rejected;
    await rToken.transferFrom(web3.eth.accounts[1], web3.eth.accounts[0], 0, {from: web3.eth.accounts[1]}).should.not.rejected;
    (await rToken.balanceOf(web3.eth.accounts[0])).should.bignumber.and.equal(4);
    (await rToken.balanceOf(web3.eth.accounts[1])).should.bignumber.and.equal(2);
    
  });

  it("Should not throw on transfer after release", async function(){
    let rToken = await ReleasableToken.new({from: web3.eth.accounts[0]});
    await rToken.mint(web3.eth.accounts[1], 3).should.not.rejected;
    await rToken.mint(web3.eth.accounts[0], 3).should.not.rejected;

    await rToken.setReleaseAgent(web3.eth.accounts[1]).should.not.rejected;
    await rToken.releaseTokenTransfer({from: web3.eth.accounts[1]}).should.not.rejected;
    await rToken.transfer(web3.eth.accounts[0], 1, {from: web3.eth.accounts[1]}).should.not.rejected;
    await rToken.transferFrom(web3.eth.accounts[1], web3.eth.accounts[0], 0, {from: web3.eth.accounts[1]}).should.not.rejected;
    (await rToken.balanceOf(web3.eth.accounts[0])).should.bignumber.and.equal(4);
    (await rToken.balanceOf(web3.eth.accounts[1])).should.bignumber.and.equal(2);
    await rToken.transfer(web3.eth.accounts[1], 1, {from: web3.eth.accounts[0]}).should.not.rejected;
    await rToken.transferFrom(web3.eth.accounts[0], web3.eth.accounts[1], 0, {from: web3.eth.accounts[0]}).should.not.rejected;
    (await rToken.balanceOf(web3.eth.accounts[0])).should.bignumber.and.equal(3);
    (await rToken.balanceOf(web3.eth.accounts[1])).should.bignumber.and.equal(3);
    
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