import flask, flask_sqlalchemy;
from flask import Flask;
from flask_sqlalchemy import SQLAlchemy;

app = Flask(__name__, static_url_path='/static'); # Remove static_url_path if CDN is being used for static files.
app.secret_key = "\xf9\x8d\xe7WN\xd0\xd2%Q`\\\xc0\xe2DN\xd15E\x8aS\x1e\xccQ\x12\x8b\x9a\xd9\xd7\xae6'5";
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://passman@localhost:3306/passwords'; # Path to database
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False;
db = SQLAlchemy(app);