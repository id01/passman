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

# Class for a single connection
class connection:
	# Initialization
	def __init__(self, myConn, myUsername):
		self.conn = myConn;
		self.userhash = hashlib.sha256(myUsername).hexdigest();

	# Functions to add and get passwords
	def add_password(self, account):
		# Make sure the account doesn't exist
		if self.get_password(account) != "de":
			return 4; # Already exists!
		# Hash all the things
		accounthash = hashlib.md5(account).hexdigest();
		# Get user ECC key
		dbc.execute("SELECT public FROM cryptokeys WHERE userhash='" + self.userhash + "'")
		try:
			pubraw = dbc.fetchone()[0];
		except (IndexError, TypeError):
			return 1; # User doesn't exist
		# Decode elliptic public key
		eccpubs = decode64(pubraw);
		eccpub = serialization.load_der_public_key(eccpubs, backend=backend);
		# Create a challenge. Get signature.
		challenge = os.urandom(20);
		self.conn.send("CHALLENGE " + encode64(challenge) + "\n");
		# Get user to insert encrypted password into database, with signature of password and challenge
		try:
			rawInput = self.conn.recv(4096).split('\n');
			passwordcrypt = rawInput[0];
			passwordsign = decode64(rawInput[1]);
		except (AttributeError, IndexError):
			return 2; # Invalid input
		if not (verifyECDSA(eccpub, passwordsign, challenge+passwordcrypt) and isBase64(passwordcrypt)):
			return 3; # Wrong signature or invalid password
		# Insert into database
		dbc.execute("INSERT into " + self.userhash + " (account, encrypted) VALUES ('" + accounthash + "', '" + passwordcrypt + "')");
		db.commit();
		return 0;

	def get_password(self, account):
		# Get user ECC key
		dbc.execute("SELECT public FROM cryptokeys WHERE userhash='" + self.userhash + "'")
		try:
		        pubraw = dbc.fetchone()[0];
		except (IndexError, TypeError):
		        return ""; # User doesn't exist
		# Decode elliptic public key
		eccpub = decode64(pubraw);
		dbc.execute("SELECT encrypted FROM " + self.userhash + " WHERE account='" + hashlib.md5(account).hexdigest() + "';");
		try:
			f = dbc.fetchone()[0];
		except (IndexError, TypeError):
			return "de"; # Entry doesn't exist
		return f;

	def get_ecckey(self):
		# Get encrypted ECC private key
		dbc.execute("select private from cryptokeys where userhash='" + self.userhash + "'");
		try:
			return dbc.fetchone()[0];
		except IndexError:
			return "";

	def get_pubkey(self):
		# Get plaintext ECC public key
		dbc.execute("select public from cryptokeys where userhash='" + self.userhash + "'");
		try:
			return dbc.fetchone()[0];
		except IndexError:
			return "";

# Main
def main(conn):
	# Get command and username, initialize connection object
	rawInput = conn.recv(1024).split('\n');
	if not rawInput:
		return;
	command = rawInput[0];
	userin = rawInput[1];
	connObj = connection(conn, userin);
	# Parse commands
	resultStr = "An unknown error occured.";
	if command == 'ADD':
		account = rawInput[2];
		result = connObj.add_password(account);
		if result == 0:
			resultStr = "Success!";
		elif result == 1:
			resultStr = "User doesn't exist in the database.";
		elif result == 2:
			resultStr = "Invalid input.";
		elif result == 3:
			resultStr = "Signature invalid.";
		elif result == 4:
			resultStr = "Password already exists!";
	elif command == 'GET':
		account = rawInput[2];
		encpass = connObj.get_password(account);
		if encpass == "":
			resultStr = "User doesn't exist";
		elif encpass == "de":
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

class RequestHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		sys.stderr.write(self.client_address[0] + " connected.\n");
		conn = self.request;
		conn.settimeout(1);
		main(conn);
		conn.shutdown(socket.SHUT_RDWR);
		conn.close();

sserver = SocketServer.TCPServer(('0.0.0.0', 3000), RequestHandler); # This port must be changed along with that in getpass.php
sserver.serve_forever();
