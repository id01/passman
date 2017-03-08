import base64;
from base64 import b64encode as encode64;
from base64 import b64decode as decode64;
import pyelliptic;
import hashlib;
import socket;
import os;
import random;
import getpass;

# Where to connect
host = "192.168.1.3"
port = 3000

username = raw_input("Username: ");
masterkey = getpass.getpass("Master Key: ");

# Get hash of the master key. Used for decryption and encryption later on.
keyhash = hashlib.sha256(masterkey).digest();

# First, I need to get the cipher and curve
def get_algs():
	remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
	remote.connect((host, port));
	remote.sendall("GETALG\n" + username + "\n");
	data = remote.recv(256) + remote.recv(256);
	remote.close();
	return data.split('\n');

print "Getting cipher and curve from the server...";
get_algs_result = get_algs();
try:
	aescipher = get_algs_result[1];
	ecccurve = get_algs_result[0];
except IndexError:
	print "User doesn't exist";
	exit(1);
print "AES Cipher: " + aescipher
print "ECC Curve: " + ecccurve
if aescipher == "" or ecccurve == "":
	print "User doesn't exist";
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
		print "Username wasn't found in the database."
		exit(1);
	# Decrypt the ECC private key
	eccenc = decode64(eccraw.strip()[6:]);
	aes = pyelliptic.Cipher(keyhash, eccenc[-16:], 0, ciphername=aescipher);
	eccpriv = aes.ciphering(eccenc[:-16]);
	print "Successfully decrypted ECC key."
	return eccpriv;

# Verify password using get_eccpriv()
try:
	get_eccpriv();
except Exception:
	print "Password incorrect.";
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
		print "Username wasn't found in the database."
		exit(1);
	eccpub = decode64(eccraw.strip()[6:]);
	return eccpub;

# Function to handshake with server
def handshake(remote, eccpriv, eccpub):
	# Get challenge and sign it
	challenge = get_sockline(remote);
	if challenge[:9] != "CHALLENGE":
		print challenge; # Some error happened.
		return 1;
	challengeresponse = encode64(pyelliptic.ECC(pubkey=eccpub, privkey=eccpriv, curve=ecccurve).sign(challenge.strip()[10:]));
	remote.send(challengeresponse + "\n");
	# Get result, see if response was accepted
	result = get_sockline(remote);
	if result[:5] != "VALID":
		print result; # Some error happened
		return 1;
	return 0;

# Function to add something to database
def add_password(account):
	# I need the ecc key
	eccpriv = get_eccpriv();
	eccpub = get_eccpub();
	# Connect to server. Request transmission
	print "Initiating connection with server...";
	remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
	remote.connect((host, port));
	remote.send("ADD\n" + account + "\n" + username + "\n");
	# Perform handshake
	print "Responding to challenge...";
	handshakeresult = handshake(remote, eccpriv, eccpub);
	if handshakeresult == 1:
		return 1; # Some error happened
	# Generate password
	print "Response accepted. Generating new password...";
	rawpassword = get_random_password(20);
	# Encrypt password with AES
	iv = pyelliptic.Cipher.gen_IV(aescipher);
	aes = pyelliptic.Cipher(keyhash, iv, 1, ciphername=aescipher);
	passwordcrypt = aes.update(rawpassword) + aes.final() + iv;
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
	print "Getting password from server...";
	remote = socket.socket(socket.AF_INET, socket.SOCK_STREAM);
	remote.connect((host, port));
	remote.send("GET\n" + account + "\n" + username + "\n");
	passraw = remote.recv(4096);
	remote.close();
	if passraw[:6] != "VALID ":
		print passraw; # Some error happened
		return 1;
	# Decrypt the password.
	print "Decrypting password...";
	passcrypt = decode64(passraw.strip()[6:]);
	aes = pyelliptic.Cipher(keyhash, passcrypt[-16:], 0, ciphername=aescipher);
	mypass = aes.ciphering(passcrypt[:-16]);
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
		print "Command not found.";

while True:
	main();
