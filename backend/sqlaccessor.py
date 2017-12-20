import os;
import config;
from config import app, db;

# Function to sign an integer
def sign64BitInteger(i):
	return -(1<<63 & i) | ((1<<63)-1 & i);
def sign32BitInteger(i):
	return -(1<<31 & i) | ((1<<31)-1 & i);

# Create UserCryptoKeys Model
class UserCryptoKeys(db.Model):
	__table_args__ = {'mysql_charset': 'ascii'} # There will be no base64 in UTF8
	userhash = db.Column(db.BigInteger, primary_key=True);
	public = db.Column(db.String(128), nullable=False, unique=True);
	private = db.Column(db.String(256), nullable=False, unique=True);

# Create UserPassword Model
class UserPassword(db.Model):
	__table_args__ = {'mysql_charset': 'ascii'} # There will be no base64 in UTF8
	id = db.Column(db.BigInteger, primary_key=True);
	userhash = db.Column(db.BigInteger, nullable=True);
	account = db.Column(db.Integer, nullable=True);
	encrypted = db.Column(db.String(180), nullable=False, unique=True);

# Try to create database
db.create_all();

class sqlaccessorclass:
	# Variables
	MODE_PUBLIC = 0;
	MODE_PRIVATE = 1;
	MODE_LIST = 2;

	# PrivateMode: 0 = Public, 1 = Private, 2 = Both (list)
	# Gets a UserCryptoKeys
	def UserCryptoKeys_get(self, userhashHex, privateMode):
		userhash = sign64BitInteger(int(userhashHex, 16));
		entity = UserCryptoKeys.query.filter(UserCryptoKeys.userhash == userhash).first();
		if entity:
			if privateMode == self.MODE_PUBLIC:
				return entity.public;
			elif privateMode == self.MODE_PRIVATE:
				return entity.private;
			elif privateMode == self.MODE_LIST:
				return entity;
			else:
				raise ValueError("Mode is invalid");
		else:
			raise AttributeError("User doesn't exist");

	# Gets a UserPassword
	def UserPassword_get(self, userhashHex, accountHex):
		userhash = sign64BitInteger(int(userhashHex, 16)); account = sign32BitInteger(int(accountHex, 16));
		entity = UserPassword.query.filter(UserPassword.userhash == userhash).filter(UserPassword.account == account).first();
		if entity:
			return entity.encrypted;
		else:
			raise AttributeError("Account doesn't exist");

	# Adds a UserCryptoKeys
	def UserCryptoKeys_add(self, userhashHex, eccpubs, eccencs):
		userhash = sign64BitInteger(int(userhashHex, 16));
		db.session.add(UserCryptoKeys(userhash=userhash, public=eccpubs, private=eccencs));
		db.session.commit();

	# Adds a UserPassword
	def UserPassword_add(self, userhashHex, accountHex, passwordcrypt):
		userhash = sign64BitInteger(int(userhashHex, 16)); account = sign32BitInteger(int(accountHex, 16));
		db.session.add(UserPassword(userhash=userhash, account=account, encrypted=passwordcrypt));
		db.session.commit();
