# This script sets up a new user for the database
import os;
import sys;
import getpass;
from getpass import getpass;
import base64;
import _mysql;
from base64 import b64encode as encode64;
import pyelliptic;
import hashlib;

# AES cipher, ECC curve
ecccurve = sys.argv[1];
aescipher = sys.argv[2];

# Get master symmetric key
username = raw_input("");
userhash = hashlib.sha256(username).hexdigest();
key = raw_input("");
keyhash = hashlib.sha256(key).digest();
# Generate ECC key (used for signing)
eccall = pyelliptic.ECC(curve=ecccurve);
eccprv = eccall.get_privkey();
eccpub = eccall.get_pubkey();
# Encrypt ECC private keys
iv = pyelliptic.Cipher.gen_IV(aescipher);
aes = pyelliptic.Cipher(keyhash, iv, 1, ciphername=aescipher)
eccenc = aes.update(eccprv) + aes.final() + iv;
# Connect to database
db = _mysql.connect('localhost', 'passman', "", 'passwords');
# Add user to database
try:
	db.query("create table " + userhash + " (account CHAR(32), encrypted VARCHAR(4096))");
except _mysql.OperationalError:
	print "User already exists!";
	exit(1);
db.query("insert into cryptokeys (userhash, public, private) values ('" + userhash + "', '" + encode64(eccpub) + "', '" + encode64(eccenc) + "')");
db.query("insert into algorithms (userhash, curve, aes) values ('" + userhash + "', '" + ecccurve + "', '" + aescipher + "')");
print "Success!"
