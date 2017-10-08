## Password Manager
Main module, containing server code.

## Description
This is a (no longer so) simple password manager that runs on mySQL.  
Its primary feature is that the server knows a minimal amount of data about the user.  
Account names and usernames are hashed, and passwords are encrypted.  
Passwords can be gotten through an HTTP service.  
Note: It's probably a good idea to put HTTP authentication on backend/wwwroot/setup.php.  

## Installation
### Backend Installation
Install dependencies.  
Go to backend/ and run make.  
Run python passwordservice.py to run the service.  
Replace the string specified in backend/wwwroot/setup.php with the sha256 hash of the signup password.  
Symlink backend/wwwroot to a folder in your webserver wwwroot.  
Add the user that will be running passwordservice to the group www-data. (Don't run as www-data though)  

### C++ Interface Installation
Download libscrypt from [here](https://github.com/technion/libscrypt) and build it.  
Copy libscrypt.a and libscrypt.h to desktop_interface/prototype/libscrypt.  
Change the serverURL variable in prototype.cpp to your server URL.  
Go to desktop_interface/prototype and run ./build.sh.  

## Features
Double encryption using AES-256 and Salsa20.  
Master Key and passwords never transmitted over internet.  
Server has zero knowledge of any passwords or master key or private key.  
Passwords stored on server encrypted with AES and Salsa20, generated at client side after secure elliptic-curve handshake.  
Centralized password management without need for copying any files.  

## Other Notes
ALWAYS run the registration web server over SSL. Otherwise, the world (and all your passwords) will be destroyed.  
Just kidding! But seriously. Don't run the webserver over plaintext. It's not good for your health.  
ALWAYS remember to install all dependencies, or else bad things will happen.  

## Changelog
* 10/07/2017 v0.5.0 (id01)  
	* Submodules!  
	* Note: This is now only the README for the backend.  
* 10/07/2017 v0.4.3 (id01)  
	* UI changes! Finally!  
* 10/06/2017 v0.4.2 (id01)  
	* Added ADD functionality to c++ interface.  
* 10/05/2017 v0.4.1 (id01)  
	* Completely overhauled signature mechanism. Now uses (r,s) concat signatures.  
	* No longer uses Python cryptography library for signatures, instead using a wrapper around CryptoPP.  
* 10/03/2017 v0.4.0 (id01)  
	* Finally! After three days and countless hours of screwing around with C and C++ libraries, I have finally created my C++ interface prototype!  
	* Note: Currently only supports GETing passwords.  
* 09/27/2017 v0.3.11 (id01)  
	* Fixed another programming error that caused sha256 hashes used as aes keys to be concatenated with an object (how does that even work?)  
* 09/26/2017 v0.3.10 (id01)  
	* Fixed programming error with scrypt that made it derive way too many bytes.  
	* Broke backwards compatibility.
* 09/26/2017 v0.3.9 (id01)  
	* Removed base64 library  
	* Fixed mySQLdb "MySQL server has gone away" bug after a while  
	* Fixed global/local variable bug with main function  
* 09/24/2017 v0.3.8 (id01)  
	* Removed Google CDN.  
	* Improved webextension, including auto-copy.  
* 09/24/2017 v0.3.7 (id01)  
	* You build wwwroot.  
* 09/23/2017 v0.3.6 (id01)  
	* Created webextension for the new stuff  
* (not committed) v0.3.5 (id01)  
	* Changed key derivation procedure for more security  
* (not committed) v0.3.4 (id01)  
	* Switched back from triplesec to sjcl.  
	* Rewrote sjcl encryption/decryption procedure.  
	* Used sjcl+salsa20 as well.  
	* 2 layers of encryption, less kdf iterations - faster, but less secure (compared to triplesec).  
* 09/20/2017 v0.3.3 (id01)  
	* Fixed a glitch where signups will only show after the server has been restarted.  
	* Tweaked triplesec for faster hashing, though that does mean lower resources used by an attacker.  
		* Please choose strong passwords for this program... You have one job...  
* 09/18/2017 v0.3.2 (id01)  
	* Changed SQL to use only one table for all users.  
	* Fixed a glitch where signups will only show after the server has been restarted (not really).  
* 09/18/2017 v0.3.1 (id01)  
	* Minor fixes in error messages  
	* Transferred some PHP input verification over to Python  
	* Rewrote isBase64  
	* Used %s for SQL queries  
	* Imposed a strict length limit for passwords, reducing the VARCHAR size of each user table  
	* Locked down passwordservice.py to localhost  
	* Greatly reduced load on server  
* (not committed) v0.3.0 (id01)  
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
* 09/04/2017 v0.2.3 (id01)  
	* Fixed some small things  
	* A bit of authentication with wwwroot  
	* Got ADD to work again  
	* Merged passwords.py and service.py in backend, greatly improving speed and efficiency  
* 08/29/2017 v0.2.2 (id01)  
	* Ditched tcpserver in favor of Python SocketServer  
	* Used Google CDN due to efficiency... This can be disabled.  
* 08/28/2017 v0.2.1 (id01)  
	* Made cli run off communicator, so I only need to change one file instead of two  
	* No more double-base64ing for AES encrypted stuff!  
	* Switched from PEM+base64 to DER+base64!  
	* Made another migrate script, not going to upload it because nobody needs it anyway...  
* 08/27/2017 v0.2.0 (id01)  
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
* 03/16/2017 v0.1.1 (id01)  
	* Switched AES library back to pyCrypto  
	* Added webui to get passwords and decrypt them on the client side using sjcl  
* 03/07/2017 v0.1.0 (id01)  
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
* 02/28/2017 v0.0.1 (id01)  
	* Start of project.  

## Credits
* jsrsasign (jsrsasign license)  
* JavaScript-MD5 (MIT license)  
* jQuery (MIT license)  
* sjcl (BSD 2.0 license)  
* sjcl-scrypt (BSD 2.0 license, by joe-invincible)  
* libscrypt (Other license)  
* Python, WebExtensions, Javascript, PHP, HTML, C, Shell and every other programming language I used :)  
Also, special thanks to my PC, router, Raspberry Pi, and web browser for making this possible :D Lol  
Note: Licenses for software used can be found in licenses/  

## Dependencies
* Note: None of these dependencies apply to the chrome extension.  
* CryptoPP (both server and c++ interface)  
* Python 2.x (server only)  
* Python 2.x C++ module development files (server only)  
* MySQL (server only)  
* An http server (server only)  
* openssl (c++ interface only)  
* libcurl (c++ interface only)  
* lpthread (c++ interface only)  