import hashlib;
import Crypto;
from Crypto.Cipher import AES;
from Crypto import Random;
import base64;
from base64 import b64encode as encode64;
from base64 import b64decode as decode64;

# A wrapper around pyCrypto for simplicity's sake. Uses padding and hashing and all stuff.
# Format = ciphertext + iv + hash of plaintext

# Mode must be a string formatted as "aes-bits-mode", eg "aes-128-cbc"

# Returns an encrypted AES message
def encryptAES(plaintext, key, mode):
	# I copied and pasted this.
	BS = AES.block_size;
	pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
	# Select mode
	modesplit = mode.split('-');
	if modesplit[1] == "128":
		hashalg = hashlib.md5;
	elif modesplit[1] == "256":
		hashalg = hashlib.sha256;
	else:
		raise Exception("Invalid bits");
	if modesplit[2] == "ctr":
		aesmode = AES.MODE_CTR;
	elif modesplit[2] == "cbc":
		aesmode = AES.MODE_CBC;
	elif modesplit[2] == "ofb":
		aesmode = AES.MODE_OFB;
	else:
		raise Exception("Invalid mode");
	iv = Random.new().read(AES.block_size);
	cipher = AES.new(hashalg(key).digest(), aesmode, iv);
	ciphertext = cipher.encrypt(pad(plaintext)) + iv + hashalg(plaintext).digest();
	return ciphertext;

# Returns a decrypted AES message
def decryptAES(ciphertext, key, mode):
	# I copied and pasted this.
	unpad = lambda s : s[0:-ord(s[-1])]
	# Select mode
	modesplit = mode.split('-');
        if modesplit[1] == "128":
                hashalg = hashlib.md5;
        elif modesplit[1] == "256":
                hashalg = hashlib.sha256;
        else:
                raise Exception("Invalid bits");
        if modesplit[2] == "ctr":
                aesmode = AES.MODE_CTR;
        elif modesplit[2] == "cbc":
                aesmode = AES.MODE_CBC;
        elif modesplit[2] == "ofb":
                aesmode = AES.MODE_OFB;
        else:
                raise Exception("Invalid mode");
	hashlength = len(hashalg('asdf').digest());
	hash = ciphertext[-hashlength:];
	iv = ciphertext[:-hashlength][-AES.block_size:];
	cipher = AES.new(hashalg(key).digest(), aesmode, iv);
	plaintext = unpad(cipher.decrypt(ciphertext[:-hashlength-AES.block_size]));
	if hashalg(plaintext).digest() != hash:
		raise Exception("Could not decrypt data!");
	return plaintext;
