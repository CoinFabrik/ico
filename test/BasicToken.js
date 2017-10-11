const BigNumber = web3.BigNumber;
const BasicToken = artifacts.require("../contracts/helpers/BasicTokenMock.sol");

require('chai')
  .use(require('chai-as-promised'))
  .use(require('chai-bignumber')(BigNumber))
  .should();

function delay_promise(delay) {
	return new Promise(function(resolve, reject) {
  	setTimeout(function() { resolve(); }, delay);
	});
}

contract('BasicToken', function() {
  it("Should not throw during construction", async function() {
    await (BasicToken.new()).should.not.rejectedWith('invalid opcode');
  });

  it("Should throw on invalid burns and transfers", async function(){
    let bToken = await BasicToken.new({from: web3.eth.accounts[0]});


    //No balance
    await bToken.burnTokensMock(web3.eth.accounts[0], 3).should.rejectedWith('invalid opcode');
    await bToken.burnTokensMock(web3.eth.accounts[1], 3).should.rejectedWith('invalid opcode');
    await bToken.transfer(web3.eth.accounts[0], 3).should.rejectedWith('invalid opcode');
    await bToken.transfer(web3.eth.accounts[1], 3).should.rejectedWith('invalid opcode');
    
    //Operations with less balance
    await bToken.mintInternalMock(web3.eth.accounts[0], 3).should.not.rejectedWith('invalid opcode');
    
    await bToken.burnTokensMock(web3.eth.accounts[1], 4).should.rejectedWith('invalid opcode');
    await bToken.transfer(web3.eth.accounts[1], 4).should.rejectedWith('invalid opcode');

  });

  it("Should return correct values", async function(){
    let bToken = await BasicToken.new({from: web3.eth.accounts[0]});
    
    (await bToken.balanceOf(web3.eth.accounts[1])).should.bignumber.and.equal(0);
    (await bToken.balanceOf(web3.eth.accounts[0])).should.bignumber.and.equal(0);
    await bToken.mintInternalMock(web3.eth.accounts[1], 3).should.not.rejectedWith('invalid opcode');
    await bToken.mintInternalMock(web3.eth.accounts[0], 3).should.not.rejectedWith('invalid opcode');
    (await bToken.balanceOf(web3.eth.accounts[1])).should.bignumber.and.equal(3);
    (await bToken.balanceOf(web3.eth.accounts[0])).should.bignumber.and.equal(3);
    await bToken.transfer(web3.eth.accounts[1], 1).should.not.rejectedWith('invalid opcode');
    (await bToken.balanceOf(web3.eth.accounts[1])).should.bignumber.and.equal(4);
    await bToken.burnTokensMock(web3.eth.accounts[1], 1).should.not.rejectedWith('invalid opcode');
    (await bToken.balanceOf(web3.eth.accounts[1])).should.bignumber.and.equal(3);

  });
});