const MintableToken = artifacts.require("../contracts/helpers/MintableTokenMock.sol");

const BigNumber = web3.BigNumber;

require('chai')
  .use(require('chai-as-promised'))
  .use(require('chai-bignumber')(BigNumber))
  .should();

contract('MintableToken', function(accounts) {

  it("Should throw during construction", async function() {
    // Multisig's address is 0.
    await (MintableToken.new(30, null, false)).should.be.rejectedWith('invalid opcode');
    await (MintableToken.new(30, null, true)).should.be.rejectedWith('invalid opcode');

    // Initial supply equals zero and minting cannot be done.
    await (MintableToken.new(0, accounts[1], false)).should.be.rejectedWith('invalid opcode');
  });

  it("Should place the initial supply in the correct addresses' balance", async function() {
    let token = await MintableToken.new(30, accounts[1], true);
    (await token.balanceOf(accounts[1])).should.be.bignumber.and.equal(30);
  });

  it("Should fail if anyone tries to mint", async function() {
    let token = await MintableToken.new(0, accounts[1], true);
    await token.mint(accounts[2], 30, {from: accounts[1]}).should.be.rejectedWith('invalid opcode'); 
    (await token.balanceOf(accounts[2])).should.be.bignumber.and.equal(0);
  });  

  it("Should place minted tokens in the correct place", async function() {
    let token = await MintableToken.new(0, accounts[1], true);
    await token.setMintAgent(accounts[1], true);
    await token.mint(accounts[2], 30, {from: accounts[1]}); 
    (await token.balanceOf(accounts[2])).should.be.bignumber.and.equal(30);
  });

    it("Should fail if trying to set a mint agent when it's disabled", async function() {
    let token = await MintableToken.new(50, accounts[1], false);
    await token.setMintAgent(accounts[2], true).should.be.rejectedWith('invalid opcode');
  });
});