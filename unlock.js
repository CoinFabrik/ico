for (var j = 0; j < eth.accounts.length; j++) {
	personal.unlockAccount(eth.accounts[j], "cuentahoracio0", 7200);
	console.log(web3.fromWei(eth.getBalance(eth.accounts[j]), "ether"));
}