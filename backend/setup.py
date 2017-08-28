# This script sets up a new user for the database
import sys;
import _mysql;
import MySQLdb;
import hashlib;
import cryptography;
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes;
from cryptography.hazmat.backends import default_backend;
from cryptography.hazmat.primitives import hashes;
from cryptography.hazmat.primitives.asymmetric import ec;
from cryptography.hazmat.primitives import serialization;
import os;
import base64;
backend = default_backend();

import simpleraes2;
from simpleraes2 import *;

# Get master symmetric key
username = raw_input("");
userhash = hashlib.sha256(username).hexdigest();
key = raw_input("");
# Generate ECC key (used for signing)
eccprv = ec.generate_private_key(ec.SECT571K1(), default_backend());
eccpub = eccprv.public_key();
# Export ECC keys
eccprvs = eccprv.private_bytes(encoding=serialization.Encoding.DER, format=serialization.PrivateFormat.PKCS8, encryption_algorithm=serialization.NoEncryption());
eccpubs = eccpub.public_bytes(encoding=serialization.Encoding.DER, format=serialization.PublicFormat.SubjectPublicKeyInfo);
eccencs = encryptAES(eccprvs, key);
# Connect to database
db = MySQLdb.connect(user='passman', db='passwords');
dbc = db.cursor();
# Add user to database
try:
	dbc.execute("create table " + userhash + " (account CHAR(32), encrypted VARCHAR(4096))");
	dbc.execute("insert into cryptokeys (userhash, public, private) values ('" + userhash + "', '" + base64.b64encode(eccpubs) + "', '" + eccencs + "')");
	db.commit();
except _mysql.OperationalError:
	print "User already exists!";
	exit(1);
print "Success!"
