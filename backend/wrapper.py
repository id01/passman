import time, os, hashlib, base64; # Standard libs

import flask;
from flask import Flask, session, url_for, escape, request;

import config; # Configuration Python file
from config import app; # Import app
import passwords; # Backend Python file

# CSRF Checker. HTTP_REFERER will be None if the user is from a different site
def csrfCheck(request, correct):
	if not request.referrer or not request.referrer[-len(correct):] == correct:
		raise ValueError("Referer incorrect!");

# SETUP function @ setup...
@app.route('/setup.php', methods=['POST'])
def processSetup():
	csrfCheck(request, "setup.html");
	time.sleep(1);
	try:
		passHash = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"; # SHA256 hash of password. Change this.
		if hashlib.sha256(request.form["auth"]).hexdigest() != passHash:
			return "Server password incorrect.";
		else:
			return passwords.main(passwords.commands.SETUP, request.form["userhash"], None,
				(request.form["public"], request.form["encryptedprivate"]));
	except KeyError:
		return "All fields must be specified.";

# GET function @ getpass...
@app.route('/getpass.php', methods=['POST'])
def processGet():
	csrfCheck(request, "getpass.html");
	# Some more checks, run GET
	try:
		if not (request.form["account"] and request.form["userhash"]):
			return "You need to specify both an account name and a user.";
		else:
			return passwords.main(passwords.commands.GET, request.form["userhash"], request.form["account"]);
	except KeyError:
		return "All fields must be specified.";

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
		return challenge+'\n'+passwords.main(passwords.commands.GETECC, request.form["userhash"], None);
	except KeyError:
		return "All fields must be specified.";

# ADD_VERIFY function @ addpass_verify...
@app.route('/addpass_verify.php', methods=['POST'])
def processADDVERIFY():
	csrfCheck(request, "addpass.html");
	# Some more checks, continue the session for ADD and retrieve data. Some checks, then run ADD.
	try:
		if session["userhash"] != request.form["userhash"]:
			return "Userhash invalid.";
		return passwords.main(passwords.commands.ADD, session["userhash"], session["account"],
			(session["challenge"], request.form["passwordcrypt"], request.form["signature"]));
	except KeyError:
		return "All fields must be specified.";

# Shows a template HTML page.
@app.route('/<page_name>.html', methods=['GET'])
def showStaticPage(page_name):
	with open("static/"+page_name+".html", 'r') as templateFile:
		return templateFile.read();

# Shows the index page
@app.route('/', methods=['GET'])
def showIndexPage():
	return showStaticPage('index');

# Run Main Loop in Debug Mode if running standalone
if __name__ == '__main__':
	app.run('127.0.0.1', 5000, True);
