import rlp
from eth_utils import keccak, to_checksum_address

def generate_contract_address(address, nonce):
	return to_checksum_address('0x' + keccak(rlp.encode([bytes(bytearray.fromhex(address[2:])), nonce]))[-20:].hex())