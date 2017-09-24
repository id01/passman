#!/bin/bash

# Compress and mangle javascript
echo "Compressing javascript at backend/wwwroot/javascript";
cd backend/wwwroot/javascript
uglifyjs addpass2.js --mangle sort,eval --compress dead_code=true > addpass2.min.js
uglifyjs setup.js --mangle sort,eval --compress dead_code=true > setup.min.js
uglifyjs getpass2.js --mangle sort,eval --compress dead_code=true > getpass2.min.js
uglifyjs global.js --mangle sort,eval --compress dead_code=true > global.min.js

# Create combined bootstrap
echo "Combining bootstraps";
cd ../bootstrap
cat jsrsasign.js newline md5.js newline sjcl1.js newline sjcl2.js newline sjcl_combine.js newline sjcl-scrypt.min.js > bootstrap_large.js
uglifyjs bootstrap_large.js > bootstrap.js # I'm too scared to do anything more than this
rm bootstrap_large.js

# Return
cd ../../..