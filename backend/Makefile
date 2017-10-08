JSDIR = wwwroot/javascript
BSDIR = wwwroot/bootstrap

all: ecdsalib.so $(JSDIR)/addpass2.min.js $(JSDIR)/getpass2.min.js $(JSDIR)/setup.min.js $(JSDIR)/global.min.js $(BSDIR)/bootstrap.js mysql_setup_done

ecdsalib.so: ecdsalib.cpp
	# Building ecdsalib...
	g++ ecdsalib.cpp -shared -O2 -o ecdsalib.so -fPIC -lcryptopp -lpython2.7

$(JSDIR)/addpass2.min.js: $(JSDIR)/addpass2.js
	# Building addpass2.min.js...
	uglifyjs $(JSDIR)/addpass2.js --mangle sort,eval --compress dead_code=true > $(JSDIR)/addpass2.min.js

$(JSDIR)/getpass2.min.js: $(JSDIR)/getpass2.js
	# Building getpass2.min.js...
	uglifyjs $(JSDIR)/getpass2.js --mangle sort,eval --compress dead_code=true > $(JSDIR)/getpass2.min.js

$(JSDIR)/setup.min.js: $(JSDIR)/setup.js
	# Building setup.min.js...
	uglifyjs $(JSDIR)/setup.js --mangle sort,eval --compress dead_code=true > $(JSDIR)/setup.min.js

$(JSDIR)/global.min.js: $(JSDIR)/global.js
	# Building global.min.js...
	uglifyjs $(JSDIR)/global.js --mangle sort,eval --compress dead_code=true > $(JSDIR)/global.min.js

$(BSDIR)/bootstrap.js: $(BSDIR)/newline $(BSDIR)/jquery.min.js $(BSDIR)/jsrsasign.js $(BSDIR)/md5.js $(BSDIR)/sjcl1.js $(BSDIR)/sjcl2.js $(BSDIR)/sjcl_combine.js $(BSDIR)/sjcl-scrypt.min.js
	# Building bootstrap.js...
	cat $(BSDIR)/jquery.min.js $(BSDIR)/newline > /tmp/bootstrap_large.js
	cat $(BSDIR)/jsrsasign.js $(BSDIR)/newline >> /tmp/bootstrap_large.js
	cat $(BSDIR)/md5.js $(BSDIR)/newline >> /tmp/bootstrap_large.js
	cat $(BSDIR)/sjcl1.js $(BSDIR)/newline $(BSDIR)/sjcl2.js $(BSDIR)/newline >> /tmp/bootstrap_large.js
	cat $(BSDIR)/sjcl_combine.js $(BSDIR)/newline >> /tmp/bootstrap_large.js
	cat $(BSDIR)/sjcl-scrypt.min.js >> /tmp/bootstrap_large.js
	uglifyjs /tmp/bootstrap_large.js > $(BSDIR)/bootstrap.js
	rm /tmp/bootstrap_large.js

mysql_setup_done: setup.sql
	# Doing MySQL Setup...
	# Enter MySQL Root Password:
	mysql -u root -p < setup.sql
	# Marking MySQL setup as done. To run again, remove mysql_setup_done file.
	echo "" > mysql_setup_done