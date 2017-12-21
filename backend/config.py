import flask, flask_sqlalchemy;
from flask import Flask;
from flask_sqlalchemy import SQLAlchemy;

app = Flask(__name__, static_url_path='/static'); # Remove static_url_path if CDN is being used for static files.
app.secret_key = "\xf9\x8d\xe7WN\xd0\xd2%Q`\\\xc0\xe2DN\xd15E\x8aS\x1e\xccQ\x12\x8b\x9a\xd9\xd7\xae6'5";
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://passman@localhost:3306/passwords'; # Path to database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False;
db = SQLAlchemy(app);
cdnurl = "https://cdnjs.cloudflare.com"; # Change this if CDN is being used for static files.
csp = "default-src 'self'; script-src 'self' %s" % cdnurl;
passHash = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"; # SHA256 hash of password. Change this. Default password is 'test'
passFile = None; # Writable file containing one-time-use signup hashes
secret_key = "\xec\x0b\xa4N\xce\x9a\x8e\xa6\xadd\xcd'U\xe3\xf1\xc2\x7f\x93\x15/\x10\xf1\r\t_\xc6x\x12\x1b\xa0\xe9+"; # Set this to a 256 bit randomly generated string.