import os;
import base64;
from base64 import b64encode as encode64;
from base64 import b64decode as decode64;
import random;
import _mysql;
import MySQLdb;
import cryptography;
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes;
from cryptography.hazmat.backends import default_backend;
from cryptography.hazmat.primitives import hashes;
from cryptography.hazmat.primitives.asymmetric import ec;
from cryptography.hazmat.primitives import serialization;
import hashlib;
backend = default_backend();

import simpleraes2;
from simpleraes2 import *;

# Connect to mysql server
try:
	db = MySQLdb.connect(user='passman', db='passwords');
	dbc = db.cursor();
# If database does not yet exist
except _mysql_exceptions.OperationalError:
	print "Something went wrong with contacting the database... Did you run setup.sh?"
	exit(1);

# Check if string is base64
def isBase64(s):
	try:
		if base64.b64encode(base64.b64decode(s)) == s:
			return True;
	except Exception:
		pass;
	return False;

# Functions to add and get passwords
def add_password(account, username):
	# Make sure the account doesn't exist
	if get_password(account, username) != "de":
		return 4; # Already exists!
	# Hash all the things
	accounthash = hashlib.md5(account).hexdigest();
	userhash = hashlib.sha256(username).hexdigest();
	# Get user ECC key
	dbc.execute("SELECT public FROM cryptokeys WHERE userhash='" + userhash + "'")
	try:
		pubraw = dbc.fetchone()[0];
	except (IndexError, TypeError):
		return 1; # User doesn't exist
	# Decode elliptic public key
	eccpubs = decode64(pubraw);
	eccpub = serialization.load_der_public_key(eccpubs, backend=backend);
	# Create a challenge. Get signature.
	challenge = os.urandom(20);
	print "CHALLENGE " + encode64(challenge);
	# Get user to insert encrypted password into database, with signature of password and challenge
	passwordcrypt = raw_input("");
	passwordsign = decode64(raw_input(""));
	if not (verifyECDSA(eccpub, passwordsign, challenge+passwordcrypt) and isBase64(passwordcrypt)):
		return 3; # Wrong signature or invalid password
	# Insert into database
	dbc.execute("INSERT into " + userhash + " (account, encrypted) VALUES ('" + accounthash + "', '" + passwordcrypt + "')");
	db.commit();
	return 0;

def get_password(account, username):
	# Get user hash
	userhash = hashlib.sha256(username).hexdigest();
        # Get user ECC key
        dbc.execute("SELECT public FROM cryptokeys WHERE userhash='" + userhash + "'")
        try:
                pubraw = dbc.fetchone()[0];
        except (IndexError, TypeError):
                return ""; # User doesn't exist
        # Decode elliptic public key
        eccpub = decode64(pubraw);
	dbc.execute("SELECT encrypted FROM " + userhash + " WHERE account='" + hashlib.md5(account).hexdigest() + "';");
	try:
		f = dbc.fetchone()[0];
	except (IndexError, TypeError):
		return "de"; # Entry doesn't exist
	return f;

def get_ecckey(username):
	# Get encrypted ECC private key
	dbc.execute("select private from cryptokeys where userhash='" + hashlib.sha256(username).hexdigest() + "'");
	try:
		return dbc.fetchone()[0];
	except IndexError:
		return "";

def get_pubkey(username):
	# Get plaintext ECC public key
	dbc.execute("select public from cryptokeys where userhash='" + hashlib.sha256(username).hexdigest() + "'");
	try:
		return dbc.fetchone()[0];
	except IndexError:
		return "";

# Main
def main():
	command = raw_input("").strip();
	if command == 'ADD':
		account = raw_input("").strip();
		userin = raw_input("").strip();
		result = add_password(account, userin);
		if result == 0:
			print "Success!";
		elif result == 1:
			print "User doesn't exist in the database.";
		elif result == 2:
			print "Challenge incorrect.";
		elif result == 3:
			print "Signature invalid.";
		elif result == 4:
			print "Password already exists!";
		else:
			print "An unknown error occured.";
	elif command == 'GET':
		account = raw_input("").strip();
		userin = raw_input("").strip();
		encpass = get_password(account, userin);
		if encpass == "":
			print "User doesn't exist";
		elif encpass == "de":
			print "Entry doesn't exist";
		else:
			print "VALID " + encpass;
	elif command == 'GETECC':
		account = raw_input("").strip();
		eccenc = get_ecckey(account);
		if eccenc == "":
			print "Entry doesn't exist";
		else:
			print "VALID " + eccenc;
	elif command == 'GETPUB':
		account = raw_input("").strip();
		eccpub = get_pubkey(account);
		if eccpub == "":
			print "Entry doesn't exist";
		else:
			print "VALID " + eccpub;
	else:
		print "Syntax Error";

main();
