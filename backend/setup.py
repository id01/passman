# This script sets up a new user for the database
import sys;
import _mysql;
import MySQLdb;
import os;
import base64;
import string; string_b64digits = string.digits+string.uppercase+string.lowercase+"+/=";

# Check if string is base64
def isBase64(s):
	return all(c in string_b64digits for c in s);
# Check if string is hex
def isHex(s):
	return all(c in string.hexdigits for c in s);

# Get master symmetric key
userhash = raw_input("");
eccpubs = raw_input("");
eccencs = raw_input("");
if not (isHex(userhash) and isHex(eccpubs) and isBase64(eccencs)):
	print "Username or ECC key is not correctly encoded. Please try again.";
	exit(1);
# Connect to database
db = MySQLdb.connect(user='passman', db='passwords');
dbc = db.cursor();
# Add user to database
try:
	dbc.execute("create table " + userhash + " (account CHAR(32), encrypted VARCHAR(400))");
	dbc.execute("insert into cryptokeys (userhash, public, private) values (%s, %s, %s)", (userhash, eccpubs, eccencs));
	db.commit();
except _mysql.OperationalError:
	print "User already exists!";
	exit(1);
print "Success!"
