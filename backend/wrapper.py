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
	# Some more checks, start a session for ADD and store things
	challenge = base64.b64encode(os.urandom(24));
	try:
		session["userhash"] = request.form["userhash"];
		session["challenge"] = challenge;
		session["account"] = request.form["account"];
		return Response(challenge+'\n'+passwords.main(passwords.commands.GETECC, request.form["userhash"], None),
			mimetype='text/text');
	except KeyError:
		return Response("All fields must be specified.", mimetype='text/text');

# ADD_VERIFY function @ addpass_verify...
@app.route('/addpass_verify.php', methods=['POST'])
def processADDVERIFY():
	csrfCheck(request, "addpass.html");
	# Some more checks, continue the session for ADD and retrieve data. Some checks, then run ADD.
	try:
		if session["userhash"] != request.form["userhash"]:
			return Response("Userhash invalid.", mimetype='text/text');
		else:
			return Response(passwords.main(passwords.commands.ADD, session["userhash"], session["account"],
				(session["challenge"], request.form["passwordcrypt"], request.form["signature"])),
				mimetype='text/text');
	except KeyError:
		return Response("All fields must be specified.", mimetype='text/text');

# Shows a template HTML page.
@app.route('/<page_name>.html', methods=['GET'])
def showStaticPage(page_name):
	# Do GZIP if allowed
	if os.path.isfile("html/"+page_name+".html.gz") and 'gzip' in request.headers.get('Accept-Encoding', '').lower():
		gzipping = True;
	else:
		gzipping = False;
	# If gzipping, gzip. Else, just send the file.
	if gzipping:
		with open("html/"+page_name+".html.gz", 'r') as templateFile:
			resp = Response(templateFile.read());
			resp.headers['Content-Security-Policy'] = config.csp;
			resp.headers['Content-Encoding'] = 'gzip';
			resp.headers['Vary'] = 'Accept-Encoding';
			return resp;
	else:
		with open("html/"+page_name+".html", 'r') as templateFile:
			resp = Response(templateFile.read());
			resp.headers['Content-Security-Policy'] = config.csp;
			return resp;

# Shows the index page
@app.route('/', methods=['GET'])
def showIndexPage():
	return showStaticPage('index');

# Run Main Loop in Debug Mode if running standalone
if __name__ == '__main__':
	app.run('0.0.0.0', 5000, True);
