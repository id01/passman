import pyelliptic;
import hashlib;
import socket;
import os;
import random;
import getpass;
import sys;
import simpleraes;
from simpleraes import *;

# Where to connect
host = "192.168.1.3"
port = 3000

username = raw_input("Username: ");
masterkey = getpass.getpass("Master Key: ");

# First, I need to get the cipher and curve
def get_algs():
	remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
	remote.connect((host, port));
	remote.sendall("GETALG\n" + username + "\n");
	data = remote.recv(256) + remote.recv(256);
	remote.close();
	return data.split('\n');

sys.stderr.write("Getting cipher and curve from the server...\n");
get_algs_result = get_algs();
try:
	aescipher = get_algs_result[1];
	ecccurve = get_algs_result[0];
except IndexError:
	sys.stderr.write("User doesn't exist\n");
	exit(1);
sys.stderr.write("AES Cipher: " + aescipher + "\n");
sys.stderr.write("ECC Curve: " + ecccurve + "\n");
if aescipher == "" or ecccurve == "":
	sys.stderr.write("User doesn't exist\n");
	exit(1);

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
		exit(1);
	# Decrypt the ECC private key
	eccenc = decode64(eccraw.strip()[6:]);
	eccpriv = decryptAES(eccenc, masterkey, aescipher);
	sys.stderr.write("Successfully decrypted ECC key.\n")
	return eccpriv;

# Verify password using get_eccpriv()
try:
	get_eccpriv();
except Exception:
	sys.stderr.write("Password incorrect.\n");
	exit(1);

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
		exit(1);
	eccpub = decode64(eccraw.strip()[6:]);
	return eccpub;

# Function to handshake with server
def handshake(remote, eccpriv, eccpub):
	# Get challenge and sign it
	challenge = get_sockline(remote);
	if challenge[:9] != "CHALLENGE":
		sys.stderr.write(challenge + "\n"); # Some error happened.
		return 1;
	challengeresponse = encode64(pyelliptic.ECC(pubkey=eccpub, privkey=eccpriv, curve=ecccurve).sign(challenge.strip()[10:]));
	remote.send(challengeresponse + "\n");
	# Get result, see if response was accepted
	result = get_sockline(remote);
	if result[:5] != "VALID":
		sys.stderr.write(result + "\n"); # Some error happened
		return 1;
	return 0;

# Function to add something to database
def add_password(account):
	# I need the ecc key
	eccpriv = get_eccpriv();
	eccpub = get_eccpub();
	# Connect to server. Request transmission
	sys.stderr.write("Initiating connection with server...\n");
	remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
	remote.connect((host, port));
	remote.send("ADD\n" + account + "\n" + username + "\n");
	# Perform handshake
	sys.stderr.write("Responding to challenge...\n");
	handshakeresult = handshake(remote, eccpriv, eccpub);
	if handshakeresult == 1:
		return 1; # Some error happened
	# Generate password
	sys.stderr.write("Response accepted. Generating new password...\n");
	rawpassword = get_random_password(20);
	# Encrypt password with AES
	passwordcrypt = encryptAES(rawpassword, masterkey, aescipher);
	# Sign password with ECC
	passwordsign = pyelliptic.ECC(pubkey=eccpub, privkey=eccpriv, curve=ecccurve).sign(passwordcrypt);
	# Send password and signature over, in base64
	remote.send(encode64(passwordcrypt) + "\n" + encode64(passwordsign) + "\n");
	finalresult = get_sockline(remote);
	remote.close();
	print finalresult;
	return 0;

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
		return 1;
	# Decrypt the password.
	sys.stderr.write("Decrypting password...\n");
	passcrypt = decode64(passraw.strip()[6:]);
	mypass = decryptAES(passcrypt, masterkey, aescipher);
	print "Password: " + mypass;
	return 0;

def main():
	command = raw_input("passman > ");
	if command[:4] == "GET ":
		get_password(command[4:]);
	elif command[:4] == "ADD ":
		add_password(command[4:]);
	elif command[:4] == "QUIT" or command[:4] == "quit":
		exit(0);
	else:
		sys.stderr.write("Command not found.\n");

while True:
	main();
