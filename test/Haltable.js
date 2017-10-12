const BigNumber = web3.BigNumber;
const Haltable = artifacts.require("../contracts/Haltable.sol");
var haltable;

require('chai')
  .use(require('chai-as-promised'))
  .use(require('chai-bignumber')(BigNumber))
  .should();

function delay_promise(delay) {
	return new Promise(function(resolve, reject) {
  	setTimeout(function() { resolve(); }, delay);
	});
}

contract('Haltable', function() {
  it("Should not throw during construction", async function() {
    await (Haltable.new()).should.not.be.rejectedWith('invalid opcode');
  });

  it("Should return correct values", async function(){
  	haltable = await (Haltable.new({from: web3.eth.accounts[0]}));
  	//(3).should.be.equal(3);
  	(await haltable.halted()).should.be.equal(false);
  	await haltable.halt({from: web3.eth.accounts[0]});
  	//await delay_promise(5000);
  	//await (console.log(await haltable.halted()));
  	(await haltable.halted()).should.be.equal(true);
  	await haltable.unhalt({from: web3.eth.accounts[0]});
  	(await haltable.halted()).should.be.equal(false);
  	await haltable.halt({from: web3.eth.accounts[1]}).should.rejected;
  	(await haltable.halted()).should.be.equal(false);
  });
});