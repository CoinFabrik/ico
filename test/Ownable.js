var Ownable = artifacts.require('../contracts/helpers/OwnableMock.sol');

require('chai')
.use(require('chai-as-promised'))
.should();

contract('Ownable', function(accounts) {
  let ownable;

  beforeEach(async function() {
    ownable = await Ownable.new();
  });

  it('Should have an owner', async function() {
    (await ownable.owner()).should.equal(accounts[0]);
  });

  it('Should change owner', async function() {
    await ownable.transferOwnership(accounts[1]);
    (await ownable.owner()).should.equal(accounts[1]);
  });

  it('should prevent non-owners from transfering', async function() {
    await (ownable.owner()).should.not.equal(accounts[2]);
    await (ownable.transferOwnership(accounts[2], {from: accounts[2]})).should.be.rejectedWith('invalid opcode');
  });

  it('should guard ownership against stuck state', async function() {
    let originalOwner = await ownable.owner();
    await (ownable.transferOwnership(null, {from: originalOwner})).should.be.rejectedWith('invalid opcode');
  });
});