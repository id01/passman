# This script sets up a new user for the database
import sys;
import _mysql;
import pyelliptic;
import hashlib;
import Crypto;
from Crypto.Cipher import AES;
from Crypto import Random;
import simpleraes;
from simpleraes import *;

# AES cipher, ECC curve
ecccurve = sys.argv[1];
aescipher = sys.argv[2];

# Get master symmetric key
username = raw_input("");
userhash = hashlib.sha256(username).hexdigest();
key = raw_input("");
# Generate ECC key (used for signing)
eccall = pyelliptic.ECC(curve=ecccurve);
eccprv = eccall.get_privkey();
eccpub = eccall.get_pubkey();
# Encrypt ECC private keys
eccenc = encryptAES(eccprv, key, aescipher);
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
