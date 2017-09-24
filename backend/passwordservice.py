import os;
import sys;
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
import SocketServer;
import socket;
import traceback;
import string; string_b64digits = string.digits+string.uppercase+string.lowercase+"+/=";
backend = default_backend();

# Connect to mysql server
try:
	db = MySQLdb.connect(user='passman', db='passwords');
# If database does not yet exist
except _mysql_exceptions.OperationalError:
	print "Something went wrong with contacting the database... Did you run setup.sh?"
	exit(1);

# Returns true if ecdsa signature is valid, false if otherwise
def verifyECDSA(public_key, signature, toverify):
	verifier = public_key.verifier(signature, ec.ECDSA(hashes.SHA256()));
	verifier.update(toverify);
	try:
		return verifier.verify();
	except cryptography.exceptions.InvalidSignature:
		return False;

# Check if string is base64
def isBase64(s):
	return all(c in string_b64digits for c in s);
# Check if string is hex
def isHex(s):
	return all(c in string.hexdigits for c in s);

# Class for a single connection
class connection:
	# Initialization
	def __init__(self, myConn, myUserhash):
		# Initalize Variables
		self.conn = myConn;
		self.addsession_challenge = None; # Session for adding a key (challenge)
		self.addsession_accounthash = None; # Session for adding a key (hash)
		self.dbc = db.cursor(); # Cursor on database connection
		# Get user ECC key
		try:
			self.userhash = [myUserhash][not isHex(myUserhash)]; # Verify hexness of myUserhash before assignment
			self.dbc.execute("SELECT public FROM cryptokeys WHERE userhash=%s", (self.userhash,))
			self.public_der_hex = self.dbc.fetchone()[0];
		except (IndexError, TypeError):
			raise ValueError("User doesn't exist"); # User doesn't exist

	# Add password - Part 1: Setup
	def add_password_1(self, accounthash, challenge):
		# Make sure the account doesn't exist
		if self.get_password(accounthash) != "":
			return False; # Already exists!
		# Hash all the things
		self.addsession_accounthash = accounthash;
		# Import the challenge.
		self.addsession_challenge = challenge;
		return True;

	# Add password - Part 2: Verify and Insert
	def add_password_2(self, rawInput):
		# Get signature.
		public_der = self.public_der_hex.decode('base64');
		eccpub = serialization.load_der_public_key(public_der, backend=backend);
		try:
			passwordcrypt = rawInput[0];
			passwordsign = decode64(rawInput[1]);
		except (AttributeError, IndexError):
			return 1; # Invalid input
		if not (verifyECDSA(eccpub, passwordsign, self.addsession_challenge+'$'+self.addsession_accounthash+'$'+passwordcrypt) and isBase64(passwordcrypt)):
			return 2; # Wrong signature or invalid password
		# Insert into database
		try:
			self.dbc.execute("INSERT into passwords (userhash, account, encrypted) VALUES (%s, %s, %s)", (self.userhash, self.addsession_accounthash, passwordcrypt));
		except MySQLdb.DataError:
			return 3; # Password too long
		return 0;

	# Function to add password
	def add_password(self, account):
		if self.add_password_1(account, os.urandom(20)):
			return self.add_password_2(self.conn.recv(4096).split('\n'));
		else:
			return -1;

	# PHP alternative to add password
	def add_password_PHP(self, account, challenge, rawInput):
		if self.add_password_1(account, challenge):
			return self.add_password_2(rawInput);
		else:
			return -1;

	# Function to get password
	def get_password(self, account):
		# Get password
		self.dbc.execute("SELECT encrypted FROM passwords WHERE account=%s AND userhash=%s", (account, self.userhash));
		try:
			f = self.dbc.fetchone()[0];
		except (IndexError, TypeError):
			return ""; # Entry doesn't exist
		return f;

	def get_ecckey(self):
		# Get encrypted ECC private key
		self.dbc.execute("select private from cryptokeys where userhash=%s", (self.userhash,));
		try:
			return self.dbc.fetchone()[0];
		except IndexError:
			return "";

	def get_pubkey(self):
		# This has been gotten during init
		return self.public_der_hex;

# Main
def main(conn, clientip):
	# Get command and username, initialize connection object, return if it doesn't exist
	rawInput = conn.recv(1024).split('\n');
	if not rawInput:
		return;
	command = rawInput[0];
	userin = rawInput[1];
	try:
		connObj = connection(conn, userin);
	except ValueError:
		resultStr = "User doesn't exist.";
		conn.send(resultStr+'\n');
		return;
	# Parse commands
	try:
		resultStr = "An unknown error occured.";
		if command == 'ADD':
			account = rawInput[2];
			result = connObj.add_password(account);
			if result == 0:
				resultStr = "Success!";
			elif result == 1:
				resultStr = "Invalid input.";
			elif result == 2:
				resultStr = "Signature invalid.";
			elif result == 3:
				resultStr = "Password already exists!";
		elif command == 'ADDP' and clientip == '127.0.0.1':
			account = rawInput[2];
			challenge = rawInput[3];
			result = connObj.add_password_PHP(account, challenge, rawInput[4:]);
			if result == 0:
				resultStr = "Success!";
			elif result == 1:
				resultStr = "Invalid input.";
			elif result == 2:
				resultStr = "Signature invalid.";
			elif result == 3:
				resultStr = "Password too long.";
			elif result == -1:
				resultStr = "Password already exists!";
		elif command == 'GET':
			account = rawInput[2];
			encpass = connObj.get_password(account);
			if encpass == "":
				resultStr = "Entry doesn't exist";
			else:
				resultStr = "VALID " + encpass;
		elif command == 'GETECC':
			eccenc = connObj.get_ecckey();
			if eccenc == "":
				resultStr = "Entry doesn't exist";
			else:
				resultStr = "VALID " + eccenc;
		elif command == 'GETPUB':
			eccpub = connObj.get_pubkey();
			if eccpub == "":
				resultStr = "Entry doesn't exist";
			else:
				resultStr = "VALID " + eccpub;
		else:
			resultStr = "Syntax Error";
		conn.send(resultStr+'\n');
		db.commit();
	except Exception as ex:
		db.rollback();
		sys.stderr.write("Caught exception {}\n".format(ex));
		traceback.print_exc();
	connObj.dbc.close();

class RequestHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		sys.stderr.write(self.client_address[0] + " connected.\n");
		conn = self.request;
		conn.settimeout(1);
		main(conn, self.client_address[0]);
		conn.shutdown(socket.SHUT_RDWR);
		conn.close();

sserver = SocketServer.TCPServer(('127.0.0.1', 3000), RequestHandler); # This port must be changed along with that in getpass.php
sserver.serve_forever();
