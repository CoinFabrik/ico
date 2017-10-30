const BigNumber = web3.BigNumber;
const From = artifacts.require("../contracts/helpers/toBeUpgraded.sol");
const To = artifacts.require("../contracts/helpers/toUpgrade.sol");

/**
 * From iherits from UpgradableToken and BasicToken to be able to test the
 * UpgradableToken's functions. Its constructor assigns to the callers address
 * the passed value. It doesn't provide another method of assigning or transfering 
 * tokens to avoid mistakes.
 *
 * To is an inherits solely from UpgradeAgent and only implemets upgradeFrom
 * to avoid errors it doesn't do anything. It's constructor uses the value it
 * receives to use as originalTokens.
 *
 */

require('chai')
  .use(require('chai-as-promised'))
  .use(require('chai-bignumber')(BigNumber))
  .should();

contract('ReleasableToken', function() {

  it("Should not throw on init", async function(){
    let initial_value = 15000;

    await From.new(initial_value, {from: web3.eth.accounts[0]}).should.not.rejected;
  });

  it("Should not fail on change of master from current master", async function(){
    let initial_value = 15000;
    let from = await From.new(initial_value, {from: web3.eth.accounts[0]});

    await  from.changeUpgradeMaster(web3.eth.accounts[1]).should.not.rejected;
    (await from.upgradeMaster()).should.equal(web3.eth.accounts[1]);
  });

  it("Should fail on change of master from non current master", async function(){
    let initial_value = 15000;
    let from = await From.new(initial_value, {from: web3.eth.accounts[0]});

    await  from.changeUpgradeMaster(web3.eth.accounts[1], {from: web3.eth.accounts[1]}).should.rejectedWith('invalid opcode');
    (await from.upgradeMaster()).should.equal(web3.eth.accounts[0]);
  });

  it("Should not throw at assigning valid agent", async function(){
    let initial_value = 15000;
    let from = await From.new(initial_value, {from: web3.eth.accounts[0]});
    let to = await To.new(initial_value, {from: web3.eth.accounts[0]});

    await from.setUpgradeAgent(to.address).should.not.rejected;
    
  });

  it("Should throw at assigning invalid agent", async function(){
    let initial_value = 15000;
    let from = await From.new(initial_value, {from: web3.eth.accounts[0]});
    let to = await To.new(initial_value+3, {from: web3.eth.accounts[0]});

    await from.setUpgradeAgent(to.address).should.rejectedWith('invalid opcode');
    await from.setUpgradeAgent('0x0').should.rejectedWith('invalid opcode');
    await from.setUpgradeAgent(web3.eth.accounts[1]).should.rejectedWith('invalid opcode');
    
  });

  it("Should throw at assigning when can't upgrade", async function(){
    let initial_value = 15000;
    let from = await From.new(initial_value, {from: web3.eth.accounts[0]});
    let to = await To.new(initial_value, {from: web3.eth.accounts[0]});

    await from.setCanUp(false);
    await from.setUpgradeAgent(to.address).should.rejectedWith('invalid opcode');
    
  });

  it("Should throw at assigning when caller not Master", async function(){
    let initial_value = 15000;
    let from = await From.new(initial_value, {from: web3.eth.accounts[0]});
    let to = await To.new(initial_value, {from: web3.eth.accounts[0]});

    await from.setUpgradeAgent(to.address, {from: web3.eth.accounts[1]}).should.rejectedWith('invalid opcode');
    
  });

  it("Should throw at assigning while upgrading", async function(){
    let initial_value = 15000;
    let from = await From.new(initial_value, {from: web3.eth.accounts[0]});
    let to = await To.new(initial_value, {from: web3.eth.accounts[0]});
    let to2 = await To.new(initial_value, {from: web3.eth.accounts[0]});

    await from.setUpgradeAgent(to.address);
    await from.upgrade(1);
    await from.setUpgradeAgent(to2.address).should.rejectedWith('invalid opcode');

    
  });

  it("Should show correct state", async function(){
    let initial_value = 15000;
    let from = await From.new(initial_value, {from: web3.eth.accounts[0]});
    let to = await To.new(initial_value, {from: web3.eth.accounts[0]});

    //Bignumber handles correctly enum objects
    //Maping: {0: Unknown, 1: NotAllowed, 2: WaitingForAgent, 3: ReadyToUpgrade, 4: Upgrading}
    await from.setCanUp(false);
    (await from.getUpgradeState()).should.bignumber.and.equal(1);
    await from.setCanUp(true);
    (await from.getUpgradeState()).should.bignumber.and.equal(2);
    await from.setUpgradeAgent(to.address);
    (await from.getUpgradeState()).should.bignumber.and.equal(3);
    await from.upgrade(1);
    (await from.getUpgradeState()).should.bignumber.and.equal(4);
    
  });

  it("Should show correct state", async function(){
    let initial_value = 15000;
    let from = await From.new(initial_value, {from: web3.eth.accounts[0]});
    let to = await To.new(initial_value, {from: web3.eth.accounts[0]});

    //Bignumber handles correctly enum objects
    //Maping: {0: Unknown, 1: NotAllowed, 2: WaitingForAgent, 3: ReadyToUpgrade, 4: Upgrading}
    await from.setCanUp(false);
    (await from.getUpgradeState()).should.bignumber.and.equal(1);
    await from.setCanUp(true);
    (await from.getUpgradeState()).should.bignumber.and.equal(2);
    await from.setUpgradeAgent(to.address);
    (await from.getUpgradeState()).should.bignumber.and.equal(3);
    await from.upgrade(1);
    (await from.getUpgradeState()).should.bignumber.and.equal(4);
    
  });

  it("Should upgrade correctly", async function(){
    let initial_value = 15000;
    let from = await From.new(initial_value, {from: web3.eth.accounts[0]});
    let to = await To.new(initial_value, {from: web3.eth.accounts[0]});

    //Before Upgrade
    await from.setUpgradeAgent(to.address);
    (await from.totalUpgraded()).should.bignumber.and.equal(0);
    (await from.balanceOf(web3.eth.accounts[0])).should.bignumber.and.equal(initial_value);
    
    //After Upgrade
    let transfered = 57;
    await from.upgrade(transfered);
    (await from.totalUpgraded()).should.bignumber.and.equal(transfered);
    (await from.balanceOf(web3.eth.accounts[0])).should.bignumber.and.equal(initial_value-transfered);
    
  });

  it("Should not upgrade if state is incorrect", async function(){
    let initial_value = 15000;
    let from = await From.new(initial_value, {from: web3.eth.accounts[0]});
    let to = await To.new(initial_value, {from: web3.eth.accounts[0]});
    let transfered = 57;

    //Before Agent Set
    await from.upgrade(transfered).should.rejectedWith('invalid opcode');
    (await from.totalUpgraded()).should.bignumber.and.equal(0);
    (await from.balanceOf(web3.eth.accounts[0])).should.bignumber.and.equal(initial_value);
    
    //Can Update in false
    await from.setUpgradeAgent(to.address);
    await from.setCanUp(false);
    await from.upgrade(transfered).should.rejectedWith('invalid opcode');
    (await from.totalUpgraded()).should.bignumber.and.equal(0);
    (await from.balanceOf(web3.eth.accounts[0])).should.bignumber.and.equal(initial_value);
    
  });
});