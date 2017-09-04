import hashlib;
import socket;
import os;
import random;
import getpass;
import sys;
import simpleraes2;
from simpleraes2 import *;
import cryptography;
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes;
from cryptography.hazmat.backends import default_backend;
from cryptography.hazmat.primitives import hashes;
from cryptography.hazmat.primitives.asymmetric import ec;
from cryptography.hazmat.primitives import serialization;
import base64;
from base64 import b64encode as encode64;
from base64 import b64decode as decode64;
backend = default_backend();

# Where to connect
host = "192.168.1.3"
#host = "localhost"
port = 3000

def communicate(username, masterkey, command):
	# Function to get a password (base64)
	def get_random_password(length):
		# This is to satisfy all those stupid password requirements that make passwords more insecure.
		# At least 1 symbol, 1 digit, 2 lowercase and 2 uppercase letters.
		random.seed(os.urandom(1)); password = random.choice("!.");
		random.seed(os.urandom(1)); password += random.choice("0123456789");
		random.seed(os.urandom(1)); password += random.choice("abcdefghijklmnopqrstuvwxyz");
		random.seed(os.urandom(1)); password += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ");
		random.seed(os.urandom(1)); password += random.choice("abcdefghijklmnopqrstuvwxyz");
		random.seed(os.urandom(1)); password += random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ");
		# Just generate the rest from os.urandom.
		password += encode64(os.urandom(length-6)).strip('=')[:length-6].replace('/','.').replace('+','!');
		return password;

	# Function to get a line from socket
	def get_sockline(remote):
		result = remote.recv(1);
		if result == '':
			return '';
		while result[len(result)-1] != '\n':
			result += remote.recv(1);
		return result.strip('\n');

	# Function to get ECC (asymmetric) private key
	def get_eccpriv():
		# Connect to server, get the ECC private key
		remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		remote.connect((host, port));
		remote.sendall("GETECC\n" + username + "\n");
		eccraw = remote.recv(4096);
		remote.close();
		if eccraw[:5] != "VALID":
			sys.stderr.write("Username wasn't found in the database.\n");
			raise Exception("Username wasn't found in the database");
		# Decrypt the ECC private key
		eccenc = eccraw.strip()[6:];
		eccprivs = decryptAES(eccenc, masterkey);
		eccpriv = serialization.load_der_private_key(eccprivs, password=None, backend=default_backend());
		sys.stderr.write("Successfully decrypted ECC key.\n")
		return eccpriv;

	# Verify password using get_eccpriv()
	try:
		get_eccpriv();
	except socket.error:
		sys.stderr.write("Communication Error.\n");
		return "ErrMsg\x04Communication error";
	except Exception:
		sys.stderr.write("Username or Password incorrect.\n");
		return "ErrPss\x04Username or Password incorrect";

	# Function to get ECC (asymmetric) public key
	def get_eccpub():
		# Connect to server, get the ECC public key
		remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		remote.connect((host, port));
		remote.sendall("GETPUB\n" + username + "\n");
		eccraw = remote.recv(4096);
		remote.close();
		if eccraw[:5] != "VALID":
			sys.stderr.write("Username wasn't found in the database.\n")
			raise Exception("Username wasn't found in the database");
		eccpubs = decode64(eccraw.strip()[6:]);
		eccpub = serialization.load_der_public_key(eccpubs, backend=default_backend());
		return eccpub;

	# Function to add something to database
	def add_password(account, passlenraw):
		# Verify input
		passlen = int(passlenraw);
		if passlen < 8:
			return "Error: Password Length must be >= 8";
		# I need the ecc key
		try:
			eccpriv = get_eccpriv();
			eccpub = get_eccpub();
		except Exception:
			sys.stderr.write("User doesn't exist!\n");
			return "Error: User doesn't exist";
		# Connect to server. Request transmission
		sys.stderr.write("Initiating connection with server...\n");
		remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		remote.connect((host, port));
		remote.send("ADD\n" + account + "\n" + username + "\n");
		# Perform handshake
		sys.stderr.write("Inserting new password...\n");
		challenge = get_sockline(remote);
		if challenge[:9] != "CHALLENGE":
			sys.stderr.write(challenge + "\n"); # Some error happened.
			return "Error: "+challenge;
		challenge = decode64(challenge[10:]); # It's in base64
		# Generate password
		rawpassword = get_random_password(passlen);
		# Encrypt password with AES
		passwordcrypt = encryptAES(rawpassword, masterkey);
		# Sign password with ECC
		passwordsign = signECDSA(eccpriv, challenge+passwordcrypt);
		# Send password and signature over, in base64
		remote.send(passwordcrypt + "\n" + encode64(passwordsign) + "\n");
		finalresult = get_sockline(remote);
		remote.close();
		sys.stderr.write(finalresult + "\n");
		return finalresult;

	# Function to get a password from database
	def get_password(account):
		# Connect to server. Get the encrypted password.
		sys.stderr.write("Getting password from server...\n");
		remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
		remote.connect((host, port));
		remote.send("GET\n" + account + "\n" + username + "\n");
		passraw = remote.recv(4096);
		remote.close();
		if passraw[:6] != "VALID ":
			sys.stderr.write(passraw + "\n"); # Some error happened
			return "Error: " + passraw;
		# Decrypt the password.
		sys.stderr.write("Decrypting password...\n");
		passcrypt = passraw.strip()[6:];
		mypass = decryptAES(passcrypt, masterkey);
		return "Password: " + mypass;

	# Command is an argument
	commandSplit = command.split(' ');
	if commandSplit[0] == "GET":
		outMsg = "Got Password.";
		outPass = get_password(commandSplit[1]); # GET [acc]
	elif commandSplit[0] == "ADD":
		outMsg = add_password(commandSplit[2], commandSplit[1]); # ADD [len] [acc]
		outPass = get_password(commandSplit[2]);
	else:
		sys.stderr.write("Command not found.\n");
		return "Command not found.\n";

	# Return in a specific form
	if outMsg.strip() == "Error: Password already exists!":
		return "Password Already Exists!\x04"+outPass;
	elif outMsg.find("Error") == 0:
		return "ErrMsg\x04"+outMsg;
	elif outPass.find("Error") == 0:
		return "ErrPss\x04"+outPass;
	else:
		return outMsg+"\x04"+outPass;
