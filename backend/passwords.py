import os;
import sys;
import time;
import ecdsalib;
from ecdsalib import verifyECDSA;
import hashlib;
import traceback;
import string; string_b64digits = string.digits+string.uppercase+string.lowercase+"+/=";

import config;
from sqlaccessor import sqlaccessorclass;
sqlaccessor = sqlaccessorclass();

# Command aliases
commands = type('obj', (object,), {'SETUP': 1, 'ADD': 2, 'GET': 3, 'GETECC': 4, 'GETPUB': 5});

# Check if string is base64
def isBase64(s):
	return all(c in string_b64digits for c in s);
# Check if string is hex
def isHex(s):
	return all(c in string.hexdigits for c in s);

# Class for a single connection
class connection:
	# Initialization
	def __init__(self, myUserhash):
		# Initalize Variables
		self.addsession_challenge = None; # Session for adding a key (challenge)
		self.addsession_accounthash = None; # Session for adding a key (hash)
		# Get user ECC key
		try:
			self.userhash = [myUserhash][not isHex(myUserhash)]; # Verify hexness of myUserhash before assignment
			cryptokeys = sqlaccessor.UserCryptoKeys_get(self.userhash, sqlaccessor.MODE_LIST);
			self.public_der_b64 = cryptokeys.public;
			self.private_der_b64 = cryptokeys.private;
		except (IndexError, TypeError, AttributeError):
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
		public_der = self.public_der_b64.decode('base64');
		try:
			passwordcrypt = rawInput[0];
			passwordsign = rawInput[1].decode('base64');
		except (AttributeError, IndexError):
			return 1; # Invalid input
		if not (verifyECDSA(self.addsession_challenge+'$'+self.addsession_accounthash+'$'+passwordcrypt, passwordsign, public_der) and isBase64(passwordcrypt)):
			return 2; # Wrong signature or invalid password
		# Insert into database
		if len(passwordcrypt) > 179:
			return 3; # Password too long
		sqlaccessor.UserPassword_add(self.userhash, self.addsession_accounthash, passwordcrypt);
		return 0;

	# Function to add password
	def add_password(self, account, challenge, rawInput):
		if self.add_password_1(account, challenge):
			return self.add_password_2(rawInput);
		else:
			return -1;

	# Function to get password
	def get_password(self, account):
		# Get password
		try:
			return sqlaccessor.UserPassword_get(self.userhash, account);
		except AttributeError:
			return "";

	def get_ecckey(self):
		# Get encrypted ECC private key
		return self.private_der_b64;

	def get_pubkey(self):
		# This has been gotten during init
		return self.public_der_b64;

# Class for a setup connection
def setupAccount(userhash, eccpubs, eccencs):
	# Initialization
	if not (isBase64(eccpubs) and isBase64(eccencs)):
		return "Username or ECC key is not correctly encoded. Please try again.";
	# Get user ECC key to see if it exists
	try:
		sqlaccessor.UserCryptoKeys_get(userhash, sqlaccessor.MODE_LIST);
		return "User already exists!";
	except AttributeError:
		sqlaccessor.UserCryptoKeys_add(userhash, eccpubs, eccencs);
		return "Success!";

# Main
def main(command, userin, account, otherData=None):
	if not (isHex(userin) and (account == None or isHex(account))):
		return "Malformed Input.";
	resultStr = "An unknown error occured.";
	# Start connection. If it throws ValueError, the user doesn't exist.
	try:
		connObj = connection(userin);
	except ValueError:
		resultStr = False;
	# User doesn't exist. If we are not setting up, exit.
	if resultStr == False:
		if command != commands.SETUP:
			resultStr = "User doesn't exist.\n";
		elif len(otherData) != 2:
			resultStr = "Malformed request.\n";
		else:
			# Set up a new account. otherData should be an array of length 2 [eccPublic, eccEncrypted]
			sys.stderr.write("New account: %s\n" % userin);
			resultStr = setupAccount(userin, otherData[0], otherData[1])+'\n';
		return resultStr;
	# Parse commands
	try:
		if command == commands.ADD:
			# Add a password. otherData should be an array of length 3 [challenge, passwordCrypt, passwordSign]
			challenge = otherData[0];
			result = connObj.add_password(account, challenge, otherData[1:]);
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
		elif command == commands.GET:
			# Get a password. otherData is ignored.
			encpass = connObj.get_password(account);
			if encpass == "":
				resultStr = "Entry doesn't exist";
			else:
				resultStr = "VALID " + encpass;
		elif command == commands.GETECC:
			# Get an ecc private key. otherData and account are ignored.
			eccenc = connObj.get_ecckey();
			if eccenc == "":
				resultStr = "Entry doesn't exist";
			else:
				resultStr = "VALID " + eccenc;
		elif command == commands.GETPUB:
			# Get an ecc public key. otherData and account are ignored.
			eccpub = connObj.get_pubkey();
			if eccpub == "":
				resultStr = "Entry doesn't exist";
			else:
				resultStr = "VALID " + eccpub;
		elif command == commands.SETUP:
			resultStr = "User already exists!"; # If the user didn't exist, it would have been set up earlier in the code
		else:
			resultStr = "Syntax Error";
	except Exception as ex:
		sys.stderr.write("Caught exception {}\n".format(ex));
		traceback.print_exc();
		resultStr = "Server Error.";
	return resultStr+'\n';
