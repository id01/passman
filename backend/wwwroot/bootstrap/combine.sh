#!/bin/sh

# Combines all bootstraps into one file
cat jsrsasign.js newline md5.js newline sjcl1.js newline sjcl2.js newline sjcl_combine.js newline sjcl-scrypt.min.js > bootstrap_large.js
uglifyjs bootstrap_large.js > bootstrap.js
rm bootstrap_large.js