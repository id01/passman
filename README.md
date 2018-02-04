## Password Manager
Main module, containing server code.

## Description
This is a (no longer so) simple password manager that runs on SQLAlchemy (doesn't work on SQLite).  
Its primary feature is that the server knows a minimal amount of data about the user.  
Account names and usernames are hashed (quickly, though), and passwords are encrypted.  
Passwords can be gotten through an HTTP(s) service.  

## Installation
### Backend Installation
Install dependencies.  
Go to backend/setup and run make.  
Run python wrapper.py to run the service in debug mode.  
Configure stuff @ backend/config.py and set up your SQL database accordingly.  
Replace the string specified in backend/wwwroot/setup.php with the sha256 hash of the signup password.  
Use the wsgi file at backend/passman.wsgi to run on a webserver like Apache.  
Optional (after make all):  

	make addcdns # Adds CDNs from bootstraps.html in the working directory of Makefile (note: slashes need to be escaped). Modify Makefile accordingly.  
	make addgzip # Adds gzip compression for HTML templates.  

Note:  
If you want to rebuild scrypt-jane.js and scrypt-jane.wasm using emcc, this is the command I used:  

	emcc scrypt-jane.c -O3 -DSCRYPT_SALSA -DSCRYPT_SHA256 -s EXPORTED_FUNCTIONS='["_scrypt_hex"]' -s EXTRA_EXPORTED_RUNTIME_METHODS='["ccall"]' -s TOTAL_MEMORY=33554432 -o sj.js --memory-init-file 0 --closure 1  
	echo "function buildModule() {`cat sj.js` return b;} var Module = buildModule();" > scrypt-jane.js  # Note: Variable 'b' was found by opening the file and finding which var Module was assigned to. You may need to use a different variable name.  


## Features
Double encryption using AES-256 and Salsa20.  
Master Key and Plaintext never transmitted over internet.  
Server has zero knowledge of any passwords or master key or private key.  
Passwords stored on server encrypted with AES and Salsa20 are generated at client side after secure elliptic-curve handshake.  
Centralized password management without need for copying any files.  

## Other Notes
ALWAYS run the web server over SSL. Otherwise, the world (and all your passwords) will be destroyed.  
Just kidding! But seriously. Don't run the webserver over plaintext. It's not good for your health.  
ALWAYS remember to install all dependencies, or else bad things will happen.  

## Changelog
* 02/03/2018 v1.0.3  
	* Rewrote the password generation algorithm for the web UI because of those websites with stupid password requirements.  
	* Added labels and character list generation for the web UI.  
	* Some small optimizations by mangling certain global variable names.  
* 01/08/2018 v1.0.2  
	* Combined linux_cli and windows_gui to client/.  
* 12/21/2017 v1.0.1  
	* More optimizations, and Javascript is now standalone.  
	* Content-Types are now shown.  
* 12/20/2017 v1.0.0  
	* Sessionlessness (using HMACs)  
	* Scrypt hashing in browser using asm.js for major performance improvement, especially on weaker CPUs.  
		* Source code over [here](https://github.com/id01/scrypt-jane/tree/emcc)  
		* Some more minor optimizations  
* 10/21/2017 v0.7.1  
	* Some extra security stuff  
	* Some efficiency optimization (including gzipping html pages)  
	* Fixed error 500 glitch when CSRF check failed  
	* Moved passHash to config file  
	* Minor bug fixes  
	* More minor bug fixes  
* 10/19/2017 v0.7.0  
	* Moved username hashes to bigints instead of strings, increasing efficiency.  
	* Salted account hashes with usernames and made them Integers, deferring let's-crack-everyone's-account-hashes attacks.  
	* Moved the entire backend to Flask and SQLAlchemy to get rid of PHP requirement.  
	* Removed MD5 dependency. Hashing with Scrypt now.  
	* Made the same modifications to the C++ and C# as the Javascript.  
	* Almost stable now!  
	* Note: Webextension generation script is probably broken right now.  
* 10/12/2017 v0.6.1  
	* Made cpp backend more universal  
* 10/11/2017 v0.6.0  
	* Windows Form GUI done!  
	* Switched scrypt library to scrypt-jane, which seems better.  
	* Moved code in setup.py into passwordservice.py; should solve the new user not exists problem.  
	* Fixed critical security problem in which passwords would be parts of the malloc()ed RAM. I forgot to urandom(). Oops.  
	* Made some minor improvements to linux_gui.  
	* Sorry for those strange commits. Git was going weird on me.  
* 10/09/2017 v0.5.1  
	* Using 16384 iterations of Scrypt instead of 8192 iterations of Scrypt and 8192 of PBKDF2 and hashing them together.  
	* Switched to Scrypt in SJCL-Master - I just found out they had that included. And it uses bits intead of bytes.  
	* Updated Scrypt library to scrypt-jane.  
* 10/07/2017 v0.5.0  
	* Submodules!  
	* Note: This is now only the README for the backend.  
* 10/07/2017 v0.4.3  
	* UI changes! Finally!  
* 10/06/2017 v0.4.2  
	* Added ADD functionality to c++ interface.  
* 10/05/2017 v0.4.1  
	* Completely overhauled signature mechanism. Now uses (r,s) concat signatures.  
	* No longer uses Python cryptography library for signatures, instead using a wrapper around CryptoPP.  
* 10/03/2017 v0.4.0  
	* Finally! After three days and countless hours of screwing around with C and C++ libraries, I have finally created my C++ interface prototype!  
	* Note: Currently only supports GETing passwords.  
* 09/27/2017 v0.3.11  
	* Fixed another programming error that caused sha256 hashes used as aes keys to be concatenated with an object (how does that even work?)  
* 09/26/2017 v0.3.10  
	* Fixed programming error with scrypt that made it derive way too many bytes.  
	* Broke backwards compatibility.
* 09/26/2017 v0.3.9  
	* Removed base64 library  
	* Fixed mySQLdb "MySQL server has gone away" bug after a while  
	* Fixed global/local variable bug with main function  
* 09/24/2017 v0.3.8  
	* Removed Google CDN.  
	* Improved webextension, including auto-copy.  
* 09/24/2017 v0.3.7  
	* You build wwwroot.  
* 09/23/2017 v0.3.6  
	* Created webextension for the new stuff  
* (not committed) v0.3.5  
	* Changed key derivation procedure for more security  
* (not committed) v0.3.4  
	* Switched back from triplesec to sjcl.  
	* Rewrote sjcl encryption/decryption procedure.  
	* Used sjcl+salsa20 as well.  
	* 2 layers of encryption, less kdf iterations - faster, but less secure (compared to triplesec).  
* 09/20/2017 v0.3.3  
	* Fixed a glitch where signups will only show after the server has been restarted.  
	* Tweaked triplesec for faster hashing, though that does mean lower resources used by an attacker.  
		* Please choose strong passwords for this program... You have one job...  
* 09/18/2017 v0.3.2  
	* Changed SQL to use only one table for all users.  
	* Fixed a glitch where signups will only show after the server has been restarted (not really).  
* 09/18/2017 v0.3.1  
	* Minor fixes in error messages  
	* Transferred some PHP input verification over to Python  
	* Rewrote isBase64  
	* Used %s for SQL queries  
	* Imposed a strict length limit for passwords, reducing the VARCHAR size of each user table  
	* Locked down passwordservice.py to localhost  
	* Greatly reduced load on server  
* (not committed) v0.3.0  
	* Biggest update EVER (again)  
	* Rewrote most of the entire backend, making the server know even less about the user.  
		* The server now only ever knows the MD5 hash of the user's username.  
		* The server now does NOT know the user's private key at all, even during signup!  
		* The server now does NOT know the user's AES key at all, even during signup!  
	* The client now uses secp256k1 instead of secp521k1 for asymmetric encryption.  
		* This is because jsrsasign does not support any sec____k1 curves other than 256.  
	* Switched symmetric encryption algorithm from two layers of AES to Salsa20+AES+Twofish.  
		* See more at https://keybase.io/triplesec/  
	* ADD now runs completely over HTTP(s)!  
	* Increased ADD signature security by adding delimiters and by having the user sign the account as well.  
	* Shows decryption progress  
* 09/04/2017 v0.2.3  
	* Fixed some small things  
	* A bit of authentication with wwwroot  
	* Got ADD to work again  
	* Merged passwords.py and service.py in backend, greatly improving speed and efficiency  
* 08/29/2017 v0.2.2  
	* Ditched tcpserver in favor of Python SocketServer  
	* Used Google CDN due to efficiency... This can be disabled.  
* 08/28/2017 v0.2.1  
	* Made cli run off communicator, so I only need to change one file instead of two  
	* No more double-base64ing for AES encrypted stuff!  
	* Switched from PEM+base64 to DER+base64!  
	* Made another migrate script, not going to upload it because nobody needs it anyway...  
* 08/27/2017 v0.2.0  
	* Biggest update EVER  
	* Rewrote the entire backend, changing ECC/AES libraries to python cryptography  
	* Rewrote most of the entire webextension so no native messaging, and more portable too  
	* Rewrote a lot more things  
	* Added ability to choose length of password added  
	* Removed ability to choose encryption type  
	* Changed default encryption type to AES-256-GCM inside AES-256-CBC  
	* For some reason, AES is now being base64'ed 2 times instead of 1  
	* Wrote a script for myself to migrate from the previous version (not availiable on github)  
	* Changed signing portion of protocol to avoid replay attacks  
	* Note to self: I should really increase granularity...  
* 03/16/2017 v0.1.1  
	* Switched AES library back to pyCrypto  
	* Added webui to get passwords and decrypt them on the client side using sjcl  
* 03/07/2017 v0.1.0  
	* Initial Commit  
	* Registration Web UI  
	* Changed cryptography library twice to something that supports elliptic curve  
	* Redid the entire backend program 5 times, each time with a different (and better) scheme.  
	* User-chosen protocols.  
	* Lots of automatic setup scripts  
	* WebExtensions for both Chrome and Firefox (using Native Messaging)  
	* Terminal Client  
	* Signatures!!!  
	* Encryption!!!  
	* Signatures and encryption!!!  
* 02/28/2017 v0.0.1  
	* Start of project.  

## Credits
* jsrsasign (jsrsasign license)  
* jQuery (MIT license)  
* sjcl (BSD 2.0 license)  
* Python, WebExtensions, Javascript, PHP, HTML, all the Cs, Shell and every other programming language I used :)  
Also, special thanks to my PC, router, Raspberry Pi, and web browser for making this possible :D Lol  
Note: Licenses for software used can be found in licenses/  

## Dependencies
* Note: These are only the server dependencies.  
* CryptoPP  
* Python 2.x  
* Python 2.x development files  
* Python Flask  
* Python SQLAlchemy  
* Uglifyjs+Uglifycss  
* An http server  
