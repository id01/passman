import time, os, hashlib, base64; # Standard libs

import flask;
from flask import Flask, session, url_for, escape, request, Response;

import config; # Configuration Python file
from config import app; # Import app
import passwords; # Backend Python file

# CSRF Checker. HTTP_REFERER will be None if the user is from a different site
def csrfCheck(request, correct):
	if not request.referrer or not request.referrer[-len(correct):] == correct:
		flask.abort(403);

# SETUP function @ setup...
@app.route('/setup.php', methods=['POST'])
def processSetup():
	csrfCheck(request, "setup.html");
	time.sleep(1);
	try:
		if hashlib.sha256(request.form["auth"]).hexdigest() != config.passHash:
			return Response("Server password incorrect.", mimetype='text/text');
		else:
			return Response(passwords.main(passwords.commands.SETUP, request.form["userhash"], None,
				(request.form["public"], request.form["encryptedprivate"])), mimetype='text/text');
	except KeyError:
		return Response("All fields must be specified.", mimetype='text/text');

# GET function @ getpass...
@app.route('/getpass.php', methods=['POST'])
def processGet():
	csrfCheck(request, "getpass.html");
	# Some more checks, run GET
	try:
		if not (request.form["account"] and request.form["userhash"]):
			return Response("You need to specify both an account name and a user.", mimetype='text/text');
		else:
			return Response(passwords.main(passwords.commands.GET, request.form["userhash"], request.form["account"]),
				mimetype='text/text');
	except KeyError:
		return Response("All fields must be specified.", mimetype='text/text');

# ADD_CHALLENGE function @ addpass_challenge...
@app.route('/addpass_challenge.php', methods=['POST'])
def processADDCHALLENGE():
	csrfCheck(request, "addpass.html");
	# Some more checks, start a session for ADD and return the challenge, ECC encrypted private key, and hmac.
	challenge = base64.b64encode(os.urandom(24));
	try:
		eccenc = passwords.main(passwords.commands.GETECC, request.form["userhash"], None);
		addsession_hmac = passwords.main(passwords.commands.ADDCHAL, request.form["userhash"], request.form["account"], challenge);
		return Response(challenge+'\n'+eccenc+addsession_hmac, mimetype='text/text');
	except KeyError:
		return Response("All fields must be specified.", mimetype='text/text');

# ADD_VERIFY function @ addpass_verify...
@app.route('/addpass_verify.php', methods=['POST'])
def processADDVERIFY():
	csrfCheck(request, "addpass.html");
	# Continue the session for ADD.
	try:
		return Response(passwords.main(passwords.commands.ADDVERIFY, request.form["userhash"],
			request.form["account"], (request.form["challenge"], request.form["passwordcrypt"],
			request.form["signature"])), mimetype='text/text');
	except KeyError:
		return Response("All fields must be specified.", mimetype='text/text');

# Function to show a static page
def showStaticPage(page_name):
	# Do GZIP if allowed
	if os.path.isfile("html/"+page_name+".gz") and 'gzip' in request.headers.get('Accept-Encoding', '').lower():
		gzipping = True;
	else:
		gzipping = False;
	# If gzipping, gzip. Else, just send the file.
	if gzipping:
		with open("html/"+page_name+".gz", 'r') as templateFile:
			resp = Response(templateFile.read());
			resp.headers['Content-Security-Policy'] = config.csp;
			resp.headers['Content-Encoding'] = 'gzip';
			resp.headers['Vary'] = 'Accept-Encoding';
			return resp;
	else:
		with open("html/"+page_name, 'r') as templateFile:
			resp = Response(templateFile.read());
			resp.headers['Content-Security-Policy'] = config.csp;
			return resp;

# Shows a template HTML page.
@app.route('/<page_name>.html', methods=['GET'])
def showHTMLPage(page_name):
	return showStaticPage(page_name+".html");

# Shows the index page at /
@app.route('/', methods=['GET'])
def showIndexPage():
	return showStaticPage("index.html");

# Shows the scrypt-jane.wasm file at /scrypt-jane.wasm
@app.route('/scrypt-jane.js.mem', methods=['GET'])
def showJSMemFile():
	return showStaticPage("scrypt-jane.js.mem");

# Run Main Loop in Debug Mode if running standalone
if __name__ == '__main__':
	app.run('0.0.0.0', 5000, True);
elif config.secret_key == "\xec\x0b\xa4N\xce\x9a\x8e\xa6\xadd\xcd'U\xe3\xf1\xc2\x7f\x93\x15/\x10\xf1\r\t_\xc6x\x12\x1b\xa0\xe9+" or passHash == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08":
	print "Please change the password hash and secret key in the configuration file before deploying this software.";
	exit(254);
