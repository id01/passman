import os;
import sys;
import time;
import _mysql_exceptions;
import MySQLdb;
import ecdsalib;
from ecdsalib import verifyECDSA;
import hashlib;
import SocketServer;
import socket;
import traceback;
import string; string_b64digits = string.digits+string.uppercase+string.lowercase+"+/=";

# Connect to mysql server
try:
	db = MySQLdb.connect(user='passman', db='passwords');
# If database does not yet exist
except _mysql_exceptions.OperationalError:
	print "Something went wrong with contacting the database... Did you run setup.sh?"
	exit(1);

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
		try:
			passwordcrypt = rawInput[0];
			passwordsign = rawInput[1].decode('base64');
		except (AttributeError, IndexError):
			return 1; # Invalid input
		if not (verifyECDSA(self.addsession_challenge+'$'+self.addsession_accounthash+'$'+passwordcrypt, passwordsign, public_der) and isBase64(passwordcrypt)):
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

	# Function to set up an account
	def setup(self, userhash, eccpubs, eccencs):
		if not (isHex(userhash) and isBase64(eccpubs) and isBase64(eccencs)):
			return "Username or ECC key is not correctly encoded. Please try again.";
		else:
			try:
				dbc.execute("select public from cryptokeys where userhash=%s", (userhash,));
				dbc.fetchone()[0];
				print "User already exists!";
				exit(1);
			except (IndexError, TypeError):
				dbc.execute("insert into cryptokeys (userhash, public, private) values (%s, %s, %s)", (userhash, eccpubs, eccencs));
				db.commit();
		return "Success!";

# Class for a setup connection
def setupAccount(userhash, eccpubs, eccencs):
	# Initialization
	if not (isHex(userhash) and isBase64(eccpubs) and isBase64(eccencs)):
		return "Username or ECC key is not correctly encoded. Please try again.";
	# Initalize Variables
	dbc = db.cursor(); # Cursor on database connection
	# Get user ECC key to see if it exists
	try:
		dbc.execute("select public from cryptokeys where userhash=%s", (userhash,));
		dbc.fetchone()[0];
		return "User already exists!";
	except (IndexError, TypeError):
		dbc.execute("insert into cryptokeys (userhash, public, private) values (%s, %s, %s)", (userhash, eccpubs, eccencs));
		db.commit();
	return "Success!";

# Main
def main(conn):
	global db; # Why, Python?
	# Get command and username, initialize connection object, return if it doesn't exist
	rawInput = conn.recv(1024).split('\n');
	if not rawInput:
		return;
	command = rawInput[0];
	userin = rawInput[1];
	resultStr = "An unknown error occured.";
	try:
		connObj = connection(conn, userin);
	except ValueError:
		resultStr = False;
	except _mysql_exceptions.OperationalError:
		# MySQL server has gone away. Refresh it and try again.
		try:
			db = MySQLdb.connect(user='passman', db='passwords');
			connObj = connection(conn, userin);
		except ValueError:
			resultStr = False;
	if resultStr == False:
		if command != 'SETUP':
			conn.send("User doesn't exist.\n");
		elif len(rawInput) <= 3:
			conn.send("Malformed request.\n");
		else:
			sys.stderr.write("New account: %s\n" % userin);
			conn.send(setupAccount(userin, rawInput[2], rawInput[3])+'\n');
		return;
	# Parse commands
	try:
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
		elif command == 'ADDP':
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
		elif command == 'SETUP':
			resultStr = "User already exists!"; # If the user didn't exist, it would have been set up earlier in the code
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
		conn = self.request;
		conn.settimeout(1);
		main(conn);
		conn.shutdown(socket.SHUT_RDWR);
		conn.close();

try:
	os.unlink('/tmp/passmansocket');
except Exception:
	pass;
sserver = SocketServer.UnixStreamServer("/tmp/passmansocket", RequestHandler); # This port must be changed along with that in getpass.php
if os.system('chgrp www-data /tmp/passmansocket') == 1:
	print "Chgrp permission denied. Are you sure this user is in the www-data group?";
	exit(1);
os.system('chmod g+w /tmp/passmansocket');
sserver.serve_forever();
