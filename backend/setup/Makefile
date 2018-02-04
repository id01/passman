# File Input and Output dirs
JSINDIR = ../source/javascript
JSOUTDIR = ../static/javascript
NAMECACHEDIR = namecache
BSINDIR = ../source/bootstrap
BSOUTDIR = ../static/bootstrap
CSSINDIR = ../source/css
CSSOUTDIR = ../static/css
HTMLINDIR = ../templates
HTMLOUTDIR = ../html
PYDIR = ../
ROOTDIR = ../..

# This is the title for the HTML files
TITLE = Passman

# NOTE: All slashes must be escaped with a backslash. Also, this can be replaced with a path to a CDN.
STATICURL = static\/# << Make sure that hashtag has no space before it.

all: $(PYDIR)/ecdsalib.so $(JSOUTDIR)/addpassHandlers.js $(JSOUTDIR)/getpassHandlers.js $(JSOUTDIR)/setupHandlers.js $(JSOUTDIR)/index.min.js $(BSOUTDIR)/bootstrap.js $(CSSOUTDIR)/index.css $(HTMLOUTDIR)/index.html $(HTMLOUTDIR)/setup.html $(HTMLOUTDIR)/getpass.html $(HTMLOUTDIR)/addpass.html

$(PYDIR)/ecdsalib.so: ecdsalib.cpp
	# Building ecdsalib...
	g++ ecdsalib.cpp -shared -O2 -o $(PYDIR)/ecdsalib.so -fPIC -lcryptopp -lpython2.7

$(JSOUTDIR)/addpass2.min.js: $(JSINDIR)/addpass2.js $(NAMECACHEDIR)/addpass2.json
	# Building addpass2.min.js...
	cp $(NAMECACHEDIR)/addpass2.json /tmp/addpass2.json
	uglifyjs $(JSINDIR)/addpass2.js --mangle --compress dead_code=true --name-cache /tmp/addpass2.json > $(JSOUTDIR)/addpass2.min.js
	rm /tmp/addpass2.json

$(JSOUTDIR)/getpass2.min.js: $(JSINDIR)/getpass2.js $(NAMECACHEDIR)/getpass2.json
	# Building getpass2.min.js...
	cp $(NAMECACHEDIR)/getpass2.json /tmp/getpass2.json
	uglifyjs $(JSINDIR)/getpass2.js --mangle --compress dead_code=true --name-cache /tmp/getpass2.json > $(JSOUTDIR)/getpass2.min.js
	rm /tmp/getpass2.json

$(JSOUTDIR)/setup.min.js: $(JSINDIR)/setup.js $(NAMECACHEDIR)/setup.json
	# Building setup.min.js...
	cp $(NAMECACHEDIR)/setup.json /tmp/setup.json
	uglifyjs $(JSINDIR)/setup.js --mangle --compress dead_code=true --name-cache /tmp/setup.json > $(JSOUTDIR)/setup.min.js
	rm /tmp/setup.json

$(JSOUTDIR)/global.min.js: $(JSINDIR)/global.js
	# Building global.min.js...
	uglifyjs $(JSINDIR)/global.js --mangle --compress dead_code=true > $(JSOUTDIR)/global.min.js

$(JSOUTDIR)/addpassHandlers.js: $(JSINDIR)/addpassHandlers.js
	# Copying addpassHandlers.js...
	cp $(JSINDIR)/addpassHandlers.js $(JSOUTDIR)/addpassHandlers.js

$(JSOUTDIR)/getpassHandlers.js: $(JSINDIR)/getpassHandlers.js
	# Copying getpassHandlers.js...
	cp $(JSINDIR)/getpassHandlers.js $(JSOUTDIR)/getpassHandlers.js

$(JSOUTDIR)/setupHandlers.js: $(JSINDIR)/setupHandlers.js
	# Copying setupHandlers.js...
	cp $(JSINDIR)/setupHandlers.js $(JSOUTDIR)/setupHandlers.js

$(JSOUTDIR)/index.min.js: $(JSINDIR)/index.js $(JSOUTDIR)/addpass2.min.js $(JSOUTDIR)/getpass2.min.js $(JSOUTDIR)/setup.min.js $(JSOUTDIR)/global.min.js
	# Building index.js...
	echo -n "async " > /tmp/index.min.js.part1
	uglifyjs $(JSINDIR)/index.js --mangle --compress dead_code=true > /tmp/index.min.js.part2
	cat /tmp/index.min.js.part1 /tmp/index.min.js.part2 > $(JSOUTDIR)/index.min.js
	rm /tmp/index.min.js.part1 /tmp/index.min.js.part2

$(BSOUTDIR)/bootstrap.js: $(BSINDIR)/newline $(BSINDIR)/jquery.min.js $(BSINDIR)/jsrsasign.js $(BSINDIR)/sjcl.js $(BSINDIR)/sjcl-salsa.min.js $(BSINDIR)/scrypt-jane.js
	# Building bootstrap.js...
	# Modify this to add CDNs
#	cat $(BSINDIR)/jquery.min.js $(BSINDIR)/newline > /tmp/bootstrap_large.js
#	cat $(BSINDIR)/jsrsasign.js $(BSINDIR)/newline >> /tmp/bootstrap_large.js
#	cat $(BSINDIR)/sjcl.js $(BSINDIR)/newline >> /tmp/bootstrap_large.js
	cat $(BSINDIR)/sjcl-salsa.min.js $(BSINDIR)/newline >> /tmp/bootstrap_large.js
	cat $(BSINDIR)/scrypt-jane.js >> /tmp/bootstrap_large.js
	uglifyjs --mangle --compress dead_code=true /tmp/bootstrap_large.js > $(BSOUTDIR)/bootstrap.js
	rm /tmp/bootstrap_large.js

$(CSSOUTDIR)/index.css: $(CSSINDIR)/index.css $(CSSOUTDIR)/form.css $(CSSOUTDIR)/hidden.css
	# Building index.css...
	uglifycss $(CSSINDIR)/index.css > $(CSSOUTDIR)/index.css

$(CSSOUTDIR)/form.css: $(CSSINDIR)/form.css
	# Building form.css...
	uglifycss $(CSSINDIR)/form.css > $(CSSOUTDIR)/form.css

$(CSSOUTDIR)/hidden.css: $(CSSINDIR)/hidden.css
	# Building hidden.css...
	uglifycss $(CSSINDIR)/hidden.css > $(CSSOUTDIR)/hidden.css

$(HTMLOUTDIR)/index.html: $(HTMLINDIR)/index.html
	# Building index.html...
	sed "s/{{ staticURL }}/$(STATICURL)/g" $(HTMLINDIR)/index.html | sed "s/{{ title }}/$(TITLE)/g" - > $(HTMLOUTDIR)/index.html

$(HTMLOUTDIR)/setup.html: $(HTMLINDIR)/setup.html
	# Building addpass.html...
	sed "s/{{ staticURL }}/$(STATICURL)/g" $(HTMLINDIR)/setup.html | sed "s/{{ title }}/$(TITLE)/g" - > $(HTMLOUTDIR)/setup.html

$(HTMLOUTDIR)/getpass.html: $(HTMLINDIR)/getpass.html
	# Building getpass.html...
	sed "s/{{ staticURL }}/$(STATICURL)/g" $(HTMLINDIR)/getpass.html > $(HTMLOUTDIR)/getpass.html

$(HTMLOUTDIR)/addpass.html: $(HTMLINDIR)/addpass.html
	# Building addpass.html...
	sed "s/{{ staticURL }}/$(STATICURL)/g" $(HTMLINDIR)/addpass.html > $(HTMLOUTDIR)/addpass.html

.PHONY: addcdns
addcdns: bootstraps.html $(HTMLOUTDIR)/index.html $(HTMLOUTDIR)/setup.html $(HTMLOUTDIR)/getpass.html $(HTMLOUTDIR)/addpass.html
	sed -i "s/<!-- bootstraps -->/`sed 's:/:\\\\/:g' bootstraps.html | tr -d '\n'`/g" $(HTMLOUTDIR)/index.html;
	sed -i "s/<!-- bootstraps -->/`sed 's:/:\\\\/:g' bootstraps.html | tr -d '\n'`/g" $(HTMLOUTDIR)/setup.html;
	sed -i "s/<!-- bootstraps -->/`sed 's:/:\\\\/:g' bootstraps.html | tr -d '\n'`/g" $(HTMLOUTDIR)/getpass.html;
	sed -i "s/<!-- bootstraps -->/`sed 's:/:\\\\/:g' bootstraps.html | tr -d '\n'`/g" $(HTMLOUTDIR)/addpass.html;

.PHONY: addgzip
addgzip: $(HTMLOUTDIR)/index.html $(HTMLOUTDIR)/setup.html $(HTMLOUTDIR)/getpass.html $(HTMLOUTDIR)/addpass.html
	gzip -c9 $(HTMLOUTDIR)/index.html > $(HTMLOUTDIR)/index.html.gz
	gzip -c9 $(HTMLOUTDIR)/setup.html > $(HTMLOUTDIR)/setup.html.gz
	gzip -c9 $(HTMLOUTDIR)/getpass.html > $(HTMLOUTDIR)/getpass.html.gz
	gzip -c9 $(HTMLOUTDIR)/addpass.html > $(HTMLOUTDIR)/addpass.html.gz

.PHONY: debug
debug: $(JSINDIR)/global.js $(JSINDIR)/setup.js $(JSINDIR)/getpass2.js $(JSINDIR)/addpass2.js
	cp $(JSINDIR)/global.js $(JSOUTDIR)/global.min.js
	cp $(JSINDIR)/setup.js $(JSOUTDIR)/setup.min.js
	cp $(JSINDIR)/getpass2.js $(JSOUTDIR)/getpass2.min.js
	cp $(JSINDIR)/addpass2.js $(JSOUTDIR)/addpass2.min.js