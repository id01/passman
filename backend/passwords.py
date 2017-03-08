import os;
import base64;
from base64 import b64encode as encode64;
from base64 import b64decode as decode64;
import random;
import _mysql;
import _mysql_exceptions;
import pyelliptic;
import hashlib;

# Connect to mysql server
try:
	db = _mysql.connect("localhost", "passman", "", "passwords");
# If database does not yet exist
except _mysql_exceptions.OperationalError:
	print "Something went wrong with contacting the database... Did you run setup.sh?"
	exit(1);

# Function to create a challenge.
def create_password():
	return encode64(os.urandom(20)).rstrip('=')[20:];

# Functions to add and get passwords
def add_password(account, username):
	# Make sure the account doesn't exist
	if get_password(account, username) != "de":
		return 4; # Already exists!
	# Hash all the things
	accounthash = hashlib.md5(account).hexdigest();
	userhash = hashlib.sha256(username).hexdigest();
	# Get user ECC key
	db.query("SELECT public FROM cryptokeys WHERE userhash='" + userhash + "'")
	try:
		pubraw = db.use_result().fetch_row(0)[0][0];
	except IndexError:
		return 1; # User doesn't exist
	# Get ecc curve for username
	ecccurve = get_algorithms(username).split('\n')[0];
	# Decode elliptic public key
	eccpub = decode64(pubraw);
	# Create a challenge. Get signature.
	challenge = create_password();
	print "CHALLENGE " + challenge;
	challengeinput = decode64(raw_input(""));
	if pyelliptic.ECC(pubkey=eccpub, curve=ecccurve).verify(challengeinput, challenge) == False:
		return 2; # Wrong challenge
	# Get user to insert encrypted password into database, with signature
	print "VALID";
	passwordcrypt = decode64(raw_input(""));
	passwordsign = decode64(raw_input(""));
	if pyelliptic.ECC(pubkey=eccpub, curve=ecccurve).verify(passwordsign, passwordcrypt) == False:
		return 3; # Wrong signature
	# Insert into database
	db.query("INSERT into " + userhash + " (account, encrypted) VALUES ('" + accounthash + "', '" + encode64(passwordcrypt) + "')");
	return 0;

def get_password(account, username):
	# Get user hash
	userhash = hashlib.sha256(username).hexdigest();
        # Get user ECC key
        db.query("SELECT public FROM cryptokeys WHERE userhash='" + userhash + "'")
        try:
                pubraw = db.use_result().fetch_row(0)[0][0];
        except IndexError:
                return ""; # User doesn't exist
        # Decode elliptic public key
        eccpub = decode64(pubraw);
	db.query("SELECT encrypted FROM " + userhash + " WHERE account='" + hashlib.md5(account).hexdigest() + "';");
	r = db.use_result();
	try:
		f = r.fetch_row(0)[0][0];
	except IndexError:
		return "de" # Entry doesn't exist
	return f;

def get_ecckey(username):
	# Get encrypted ECC private key
	db.query("select private from cryptokeys where userhash='" + hashlib.sha256(username).hexdigest() + "'");
	try:
		return db.use_result().fetch_row(0)[0][0];
	except IndexError:
		return "";

def get_pubkey(username):
	# Get plaintext ECC public key
	db.query("select public from cryptokeys where userhash='" + hashlib.sha256(username).hexdigest() + "'");
	try:
		return db.use_result().fetch_row(0)[0][0];
	except IndexError:
		return "";

def get_algorithms(username):
	# Get algorithms, seperated by newline.
	db.query("select curve from algorithms where userhash='" + hashlib.sha256(username).hexdigest() + "'");
	try:
		a = db.use_result().fetch_row(0)[0][0];
		db.query("select aes from algorithms where userhash='" + hashlib.sha256(username).hexdigest() + "'");
		b = db.use_result().fetch_row(0)[0][0];
		return a + "\n" + b;
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
	elif command == 'GETALG':
		username = raw_input("").strip();
		print get_algorithms(username);
	else:
		print "Syntax Error";

main();
