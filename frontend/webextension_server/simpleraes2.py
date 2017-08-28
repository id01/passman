import hashlib;
import os;
import cryptography;
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes;
from cryptography.hazmat.backends import default_backend;
from cryptography.hazmat.primitives import hashes;
from cryptography.hazmat.primitives.asymmetric import ec;
from cryptography.hazmat.primitives import serialization;
import base64;
backend = default_backend();

# A wrapper around python cryptography for simplicity's sake. Uses padding and hashing and all stuff.
# Format = ciphertext + iv + hash of plaintext

# Mode must be an integer

# S = string, P = pad (true)/unpad (false)
def pkcs5(s, p):
	if p:
		return s + (16 - len(s) % 16) * chr(16 - len(s) % 16);
	else:
		return s[0:-ord(s[-1])]

# Returns an encrypted AES message
def encryptAES(plaintext, key):
	# Pad
	plaintext = pkcs5(plaintext, True);
	# Generate keys
	salt = os.urandom(8);
	shakey1 = hashlib.sha256(key).digest()[:32]; # Key 1 = sha256 of password
	shakey2 = hashlib.sha256(shakey1+salt).digest()[:32]; # Key 2 = sha256 of key 1, plus 8 known bytes as a salt
	# First encryption (AES-256-GCM, with integrity verification)
	iv = os.urandom(16);
	cipher = Cipher(algorithms.AES(shakey1), modes.GCM(iv), backend=backend).encryptor();
	ciphertext1 = iv + cipher.update(plaintext) + cipher.finalize() + cipher.tag; # Cipher.tag has length 16
	# Second encryption (AES-256-CBC, no integrity verification)
	iv = os.urandom(16);
	cipher = Cipher(algorithms.AES(shakey2), modes.CBC(iv), backend=backend).encryptor();
	ciphertext2 = iv + cipher.update(ciphertext1) + cipher.finalize() + salt; # Salt has length 8
	# Return base64
	return base64.b64encode(ciphertext2);

# Returns a decrypted AES message
def decryptAES(rawciphertext, key):
	# Decode base64
	ciphertext2 = base64.b64decode(rawciphertext);
	# Generate keys, get salt
	salt = ciphertext2[-8:]; ciphertext2 = ciphertext2[:-8];
	shakey1 = hashlib.sha256(key).digest()[:32]; # Key 1 = sha256 of password
	shakey2 = hashlib.sha256(shakey1+salt).digest()[:32]; # Key 2 = sha256 of key 1, plus 8 known bytes as a salt
	# First decryption (AES-256-CBC, no integrity verification)
	iv = ciphertext2[:16]; ciphertext2 = ciphertext2[16:];
	cipher = Cipher(algorithms.AES(shakey2), modes.CBC(iv), backend=backend).decryptor();
	ciphertext1 = cipher.update(ciphertext2) + cipher.finalize();
	# Second decryption (AES-256-GCM, with integrity verification)
	iv = ciphertext1[:16]; ciphertext1 = ciphertext1[16:];
	tag = ciphertext1[-16:]; ciphertext1 = ciphertext1[:-16];
	cipher = Cipher(algorithms.AES(shakey1), modes.GCM(iv, tag=tag), backend=backend).decryptor();
	plaintext = cipher.update(ciphertext1) + cipher.finalize();
	# Return plaintext, unpadded
	return pkcs5(plaintext, False);

# Returns an ecdsa signature
def signECDSA(private_key, tosign):
	signer = private_key.signer(ec.ECDSA(hashes.SHA256()));
	signer.update(tosign);
	return signer.finalize();

# Returns true if ecdsa signature is valid, false if otherwise
def verifyECDSA(public_key, signature, toverify):
	verifier = public_key.verifier(signature, ec.ECDSA(hashes.SHA256()));
	verifier.update(toverify);
	try:
		return verifier.verify();
	except cryptography.exceptions.InvalidSignature:
		return False;
