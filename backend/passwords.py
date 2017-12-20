import os;
import sys;
import time;
import ecdsalib;
from ecdsalib import verifyECDSA;
import hashlib, hmac;
import traceback;
import string; string_b64digits = string.digits+string.uppercase+string.lowercase+"+/=";

import config;
from sqlaccessor import sqlaccessorclass;
sqlaccessor = sqlaccessorclass();

# Command aliases
commands = type('obj', (object,), {'SETUP': 0, 'ADDCHAL': 1, 'ADDVERIFY': 2, 'GET': 3, 'GETECC': 4, 'GETPUB': 5});

# Check if string is base64
def isBase64(s):
	return all(c in string_b64digits for c in s);
# Check if string is hex
def isHex(s):
	return all(c in string.hexdigits for c in s);

# Function to combine add inputs to verify
def combineAdd(inputTuple):
	return '$'.join(inputTuple);
# Function to do an HMAC
def createHMAC(message):
	return hmac.new(config.secret_key, message, hashlib.sha256).hexdigest();

# Class for a single connection
class connection:
	# Initialization
	def __init__(self, myUserhash):
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
			return None; # Already exists!
		# Hash all the things
		addsession_hmac = createHMAC(combineAdd((challenge, self.userhash, accounthash)));
		return addsession_hmac;

	# Add password - Part 2: Verify and Insert
	def add_password_2(self, accounthash, rawInput):
		# Get all inputs.
		# Inputs should be in a tuple of format (challenge, passwordcrypt, passwordsignB64)
		public_der = self.public_der_b64.decode('base64');
		try:
			challenge = rawInput[0]; # Should be string in base64.
			passwordcrypt = rawInput[1]; # Should be string in base64 containing encrypted password.
			passwordsign = rawInput[2].decode('base64'); # Should be string in base64 containing signature.
			addsession_hmac = createHMAC(combineAdd((challenge, self.userhash, accounthash))); # Creates hex string containing HMAC.
			verifyText = combineAdd((addsession_hmac, self.userhash, accounthash, passwordcrypt)); # The user signed this string in passwordsign.
		except (AttributeError, IndexError):
			return 1; # Invalid input
		# Verify HMAC and ECDSA
		if not verifyECDSA(verifyText, passwordsign, public_der):
			return 2; # Wrong signature or wrong HMAC. Since the hacker can't forge an HMAC, a signature cannot be created of a forged HMAC.
		# Insert into database
		if len(passwordcrypt) > 179 or not isBase64(passwordcrypt):
			return 3; # Password too long or not in base64
		sqlaccessor.UserPassword_add(self.userhash, accounthash, passwordcrypt); # If everything is good, add the password.
		return 0;

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
		if command == commands.ADDCHAL:
			# Generate an add password challenge. 
			result = connObj.add_password_1(account, otherData); # otherData should be challenge.
			if result:
				resultStr = "VALID " + result;
			else:
				resultStr = "Password already exists!";
		elif command == commands.ADDVERIFY:
			# Verify the addition of a password.
			result = connObj.add_password_2(account, otherData);
			if result == 0:
				resultStr = "Success!";
			elif result == 1:
				resultStr = "Input invalid.";
			elif result == 2:
				resultStr = "Signature invalid.";
			elif result == 3:
				resultStr = "Password invalid.";
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
