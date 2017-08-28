import sys, os;
import getpass;
import hashlib;
sys.path.append(os.path.dirname(os.path.realpath(__file__))+"/webextension_server");
import communicator as com;

# Get login
username = raw_input("Username: ");
password = getpass.getpass("Master Key: ");

# Function to print syntax
def printSyntax():
	print "GET Syntax: GET [account]";
	print "ADD Syntax: ADD [password length] [account]";
printSyntax();

# Main loop
while True:
	myInput = raw_input("Passwords > ");
	command = myInput.split(' ')[0];
	if command == 'GET' or command == 'ADD':
		print com.communicate(username, password, myInput).replace("\x04", "\n");
	elif command == 'quit' or command == 'exit':
		exit(0);
	else:
		printSyntax();