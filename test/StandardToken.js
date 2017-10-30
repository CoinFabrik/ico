const BigNumber = web3.BigNumber;
const StandardToken = artifacts.require("../contracts/StandardTokenMock.sol");

require('chai')
  .use(require('chai-as-promised'))
  .use(require('chai-bignumber')(BigNumber))
  .should();

contract('Basic Token', function() {
  it("Should not throw during construction", async function() {
    await (StandardToken.new()).should.not.rejectedWith('invalid opcode');
  });

  it("Should throw on invalid burns and transfers", async function(){
    let bToken = await StandardToken.new({from: web3.eth.accounts[0]});

    //No balance
    await bToken.burnTokensMock(web3.eth.accounts[0], 3).should.rejectedWith('invalid opcode');
    await bToken.burnTokensMock(web3.eth.accounts[1], 3).should.rejectedWith('invalid opcode');
    await bToken.transfer(web3.eth.accounts[0], 3).should.rejectedWith('invalid opcode');
    await bToken.transfer(web3.eth.accounts[1], 3).should.rejectedWith('invalid opcode');
    
    //Operations with less balance
    await bToken.mint(web3.eth.accounts[0], 3).should.not.rejectedWith('invalid opcode');
    
    await bToken.burnTokensMock(web3.eth.accounts[1], 4).should.rejectedWith('invalid opcode');
    await bToken.transfer(web3.eth.accounts[1], 4).should.rejectedWith('invalid opcode');

  });

  it("Should return correct values", async function(){
    let bToken = await StandardToken.new({from: web3.eth.accounts[0]});
    
    (await bToken.balanceOf(web3.eth.accounts[1])).should.bignumber.and.equal(0);
    (await bToken.balanceOf(web3.eth.accounts[0])).should.bignumber.and.equal(0);
    await bToken.mint(web3.eth.accounts[1], 3).should.not.rejectedWith('invalid opcode');
    await bToken.mint(web3.eth.accounts[0], 3).should.not.rejectedWith('invalid opcode');
    (await bToken.balanceOf(web3.eth.accounts[1])).should.bignumber.and.equal(3);
    (await bToken.balanceOf(web3.eth.accounts[0])).should.bignumber.and.equal(3);
    await bToken.transfer(web3.eth.accounts[1], 1).should.not.rejectedWith('invalid opcode');
    (await bToken.balanceOf(web3.eth.accounts[1])).should.bignumber.and.equal(4);
    await bToken.burnTokensMock(web3.eth.accounts[1], 1).should.not.rejectedWith('invalid opcode');
    (await bToken.balanceOf(web3.eth.accounts[1])).should.bignumber.and.equal(3);

  });
});

contract('StandardToken', function(accounts) {

  beforeEach(async function() {
    token = await StandardToken.new();
    await token.mint(accounts[0], 100);
    await token.mint(accounts[1], 100);
    await token.mint(accounts[2], 100);
  });

  it("Should fail if trying to transfer without allowance", async function() {
    await token.transferFrom(accounts[1], accounts[2], 30).should.be.rejectedWith('invalid opcode');
  });

  it("Should transfer correctly if allowed", async function() {
    let balance_account0 = await token.balanceOf(accounts[0]);
    let balance_account2 = await token.balanceOf(accounts[2]);
    await token.approve(accounts[1], 30, {from: accounts[0]}).should.not.be.rejected;
    await token.transferFrom(accounts[0], accounts[2], 20, {from: accounts[1]}).should.not.be.rejected;
    (await token.balanceOf(accounts[0])).should.be.bignumber.and.equal(balance_account0.minus(20));
    (await token.balanceOf(accounts[2])).should.be.bignumber.and.equal(balance_account2.plus(20));
    await token.transferFrom(accounts[0], accounts[2], 10, {from: accounts[1]}).should.not.be.rejected;
    (await token.balanceOf(accounts[0])).should.be.bignumber.and.equal(balance_account0.minus(30));
    (await token.balanceOf(accounts[2])).should.be.bignumber.and.equal(balance_account2.plus(30));
  });

  it("Should modify allowance accordingly", async function() {
    (await token.allowance(accounts[0], accounts[2])).should.be.bignumber.and.equal(0);
    await token.addApproval(accounts[2], 30, {from: accounts[0]}).should.not.be.rejected;
    (await token.allowance(accounts[0], accounts[2])).should.be.bignumber.and.equal(30);
    await token.subApproval(accounts[2], 10, {from: accounts[0]}).should.not.be.rejected;
    (await token.allowance(accounts[0], accounts[2])).should.be.bignumber.and.equal(20);
  });

  it("Should not fail if trying to substract more than existing allowance", async function() {
    await token.addApproval(accounts[1], 5, {from: accounts[0]}).should.not.be.rejected;
    await token.subApproval(accounts[1], 10, {from: accounts[0]}).should.not.be.rejected;
    (await token.allowance(accounts[0], accounts[1])).should.be.bignumber.and.equal(0);
  });

  it("Should fail if trying to overwrite a non-zero allowance", async function() {
    await token.addApproval(accounts[1], 5, {from: accounts[0]}).should.not.be.rejected;
    await token.approve(accounts[1], 50, {from: accounts[0]}).should.be.rejectedWith('invalid opcode');
  });

  it("Should not fail if trying to allow more spending than available balance", async function() {
    let balance = await token.balanceOf(accounts[0]);
    await token.addApproval(accounts[1], balance.plus(1), {from: accounts[0]}).should.not.be.rejected;
  });

  it("Should fail if trying to transfer more than available (although allowed)", async function() {
    let balance = await token.balanceOf(accounts[0]);
    await token.addApproval(accounts[1], balance.plus(1), {from: accounts[0]}).should.not.be.rejected;
    await token.transferFrom(accounts[0], accounts[2], 101, {from: accounts[1]}).should.be.rejectedWith('invalid opcode');
  });
  
});