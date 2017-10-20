# File Input and Output dirs
JSINDIR = ../source/javascript
JSOUTDIR = ../static/javascript
BSINDIR = ../source/bootstrap
BSOUTDIR = ../static/bootstrap
CSSINDIR = ../source/css
CSSOUTDIR = ../static/css
HTMLINDIR = ../templates
HTMLOUTDIR = ../html
PYDIR = ../
ROOTDIR = ../..

# NOTE: All slashes must be escaped with a backslash. Also, this can be replaced with a path to a CDN.
STATICURL = static\/# << Make sure that hashtag has no space before it.

all: $(PYDIR)/ecdsalib.so $(JSOUTDIR)/addpass2.min.js $(JSOUTDIR)/getpass2.min.js $(JSOUTDIR)/setup.min.js $(JSOUTDIR)/global.min.js $(JSOUTDIR)/addpassHandlers.js $(JSOUTDIR)/getpassHandlers.js $(JSOUTDIR)/setupHandlers.js $(JSOUTDIR)/index.min.js $(BSOUTDIR)/bootstrap.js $(CSSOUTDIR)/index.css $(CSSOUTDIR)/form.css $(HTMLOUTDIR)/index.html $(HTMLOUTDIR)/setup.html $(HTMLOUTDIR)/getpass.html $(HTMLOUTDIR)/addpass.html

$(PYDIR)/ecdsalib.so: ecdsalib.cpp
	# Building ecdsalib...
	g++ ecdsalib.cpp -shared -O2 -o $(PYDIR)/ecdsalib.so -fPIC -lcryptopp -lpython2.7

$(JSOUTDIR)/addpass2.min.js: $(JSINDIR)/addpass2.js
	# Building addpass2.min.js...
	uglifyjs $(JSINDIR)/addpass2.js --mangle sort,eval --compress dead_code=true > $(JSOUTDIR)/addpass2.min.js

$(JSOUTDIR)/getpass2.min.js: $(JSINDIR)/getpass2.js
	# Building getpass2.min.js...
	uglifyjs $(JSINDIR)/getpass2.js --mangle sort,eval --compress dead_code=true > $(JSOUTDIR)/getpass2.min.js

$(JSOUTDIR)/setup.min.js: $(JSINDIR)/setup.js
	# Building setup.min.js...
	uglifyjs $(JSINDIR)/setup.js --mangle sort,eval --compress dead_code=true > $(JSOUTDIR)/setup.min.js

$(JSOUTDIR)/global.min.js: $(JSINDIR)/global.js
	# Building global.min.js...
	uglifyjs $(JSINDIR)/global.js --mangle sort,eval --compress dead_code=true > $(JSOUTDIR)/global.min.js

$(JSOUTDIR)/addpassHandlers.js: $(JSINDIR)/addpassHandlers.js
	# Copying addpassHandlers.js...
	cp $(JSINDIR)/addpassHandlers.js $(JSOUTDIR)/addpassHandlers.js

$(JSOUTDIR)/getpassHandlers.js: $(JSINDIR)/getpassHandlers.js
	# Copying getpassHandlers.js...
	cp $(JSINDIR)/getpassHandlers.js $(JSOUTDIR)/getpassHandlers.js

$(JSOUTDIR)/setupHandlers.js: $(JSINDIR)/setupHandlers.js
	# Copying setupHandlers.js...
	cp $(JSINDIR)/setupHandlers.js $(JSOUTDIR)/setupHandlers.js

$(JSOUTDIR)/index.min.js: $(JSINDIR)/index.js
	# Building index.js...
	echo -n "async " > /tmp/index.min.js.part1
	uglifyjs $(JSINDIR)/index.js --mangle sort,eval --compress dead_code=true > /tmp/index.min.js.part2
	cat /tmp/index.min.js.part1 /tmp/index.min.js.part2 > $(JSOUTDIR)/index.min.js
	rm /tmp/index.min.js.part1 /tmp/index.min.js.part2

$(BSOUTDIR)/bootstrap.js: $(BSINDIR)/newline $(BSINDIR)/jquery.min.js $(BSINDIR)/jsrsasign.js $(BSINDIR)/sjcl.js $(BSINDIR)/sjcl-salsa.min.js
	# Building bootstrap.js...
	# Modify this to add CDNs
	cat $(BSINDIR)/jquery.min.js $(BSINDIR)/newline > /tmp/bootstrap_large.js
	cat $(BSINDIR)/jsrsasign.js $(BSINDIR)/newline >> /tmp/bootstrap_large.js
	cat $(BSINDIR)/sjcl.js $(BSINDIR)/newline $(BSINDIR)/sjcl-salsa.min.js >> /tmp/bootstrap_large.js
	uglifyjs /tmp/bootstrap_large.js > $(BSOUTDIR)/bootstrap.js
	rm /tmp/bootstrap_large.js

$(CSSOUTDIR)/index.css: $(CSSINDIR)/index.css
	# Building index.css...
	uglifycss $(CSSINDIR)/index.css > $(CSSOUTDIR)/index.css

$(CSSOUTDIR)/form.css: $(CSSINDIR)/form.css
	# Building form.css...
	uglifycss $(CSSINDIR)/form.css > $(CSSOUTDIR)/form.css

$(HTMLOUTDIR)/index.html: $(HTMLINDIR)/index.html
	# Building index.html...
	echo "s/{{ staticURL }}/$(STATICURL)/g";
	sed "s/{{ staticURL }}/$(STATICURL)/g" $(HTMLINDIR)/index.html > $(HTMLOUTDIR)/index.html

$(HTMLOUTDIR)/setup.html: $(HTMLINDIR)/setup.html
	# Building addpass.html...
	sed "s/{{ staticURL }}/$(STATICURL)/g" $(HTMLINDIR)/setup.html > $(HTMLOUTDIR)/setup.html

$(HTMLOUTDIR)/getpass.html: $(HTMLINDIR)/getpass.html
	# Building getpass.html...
	sed "s/{{ staticURL }}/$(STATICURL)/g" $(HTMLINDIR)/getpass.html > $(HTMLOUTDIR)/getpass.html

$(HTMLOUTDIR)/addpass.html: $(HTMLINDIR)/addpass.html
	# Building addpass.html...
	sed "s/{{ staticURL }}/$(STATICURL)/g" $(HTMLINDIR)/addpass.html > $(HTMLOUTDIR)/addpass.html

.PHONY: addcdns
addcdns: bootstraps.html $(HTMLOUTDIR)/index.html $(HTMLOUTDIR)/setup.html $(HTMLOUTDIR)/getpass.html $(HTMLOUTDIR)/addpass.html
	sed -i "s/<!-- bootstrap -->/`cat bootstraps.html`/g" $(HTMLOUTDIR)/index.html;
	sed -i "s/<!-- bootstrap -->/`cat bootstraps.html`/g" $(HTMLOUTDIR)/setup.html;
	sed -i "s/<!-- bootstrap -->/`cat bootstraps.html`/g" $(HTMLOUTDIR)/getpass.html;
	sed -i "s/<!-- bootstrap -->/`cat bootstraps.html`/g" $(HTMLOUTDIR)/addpass.html;