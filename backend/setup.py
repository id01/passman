# This script sets up a new user for the database
import _mysql;
import MySQLdb;
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
if not (isHex(userhash) and isBase64(eccpubs) and isBase64(eccencs)):
	print "Username or ECC key is not correctly encoded. Please try again.";
	exit(1);
# Connect to database
db = MySQLdb.connect(user='passman', db='passwords');
dbc = db.cursor();
# Add user to database
try:
	dbc.execute("select public from cryptokeys where userhash=%s", (userhash,));
	dbc.fetchone()[0];
	print "User already exists!";
	exit(1);
except (IndexError, TypeError):
	dbc.execute("insert into cryptokeys (userhash, public, private) values (%s, %s, %s)", (userhash, eccpubs, eccencs));
	db.commit();
print "Success!"
