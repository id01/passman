## Password Manager
Note: I haven't come up with a good name yet.  
Another note: This only works on Linux as of the moment. However, it shouldn't be too hard to port the client.  
A third note: I really need to make a good UI for the webextension... Help would be appreciated :)  

## Description
This is a (no longer so) simple password manager that runs on mySQL.  
Its primary feature is that the server knows a minimal amount of data about the user (IP is logged, though).  
Account names and usernames are hashed, and passwords are encrypted.  
Passwords can be gotten through an HTTP service.  

## Installation
### Backend Installation
Install dependencies.  
Run ./setup.sh  
Run ./service.sh to start the service.  
Symlink a folder on your webserver to backend/wwwroot for setting up of new users from the internet.  
#### Optional
To remove Google CDN, download jQuery (production version) and move it to backend/wwwroot/bootstrap/jquery.js, then remove 
and uncomment the lines marked in backend/wwwroot/getpass.html.  

### Frontend Installation
Install web extension on browser. It won't work yet.  
Add 'python frontend/webextension_server/httpserver.py' to startup.  
Change "host" and "port" parameters in frontend/webextension_server/communicator.py 
to appropriate values so you can connect to the right server.  
Log out then log in.  

## Features
Variable symmetric and elliptic curve algorithms. (Including AES-256 and sect571k1)  
Master Key and passwords never transmitted over internet except initial registration over webUI.  
Server has zero knowledge of any passwords or master key, except initial registration over webUI.  
Passwords stored on server encrypted with AES and generated at client side after secure elliptic-curve handshake.  
Centralized password management without need for copying any files.  

## Other Notes
ALWAYS run the registration web server over SSL. Otherwise, the world (and all your passwords) will be destroyed.  
Just kidding! But seriously. Don't run the webserver over plaintext. It's not good for your health.  
ALWAYS remember to install all dependencies, or else bad things will happen.  

## Todo
100% HTTP/HTTPS (giving up due to lack of a good standard Javascript implementation of ecdsa)  
NOTE: You can still bypass firewalls if you host the service on port 80 :)  

## Changelog
* 08/29/2017 v1.1.1 (id01)  
 * Ditched tcpserver in favor of Python SocketServer  
 * Used Google CDN due to efficiency... This can be disabled.  
* 08/28/2017 v1.1.0 (id01)  
 * Made cli run off communicator, so I only need to change one file instead of two  
 * No more double-base64ing for AES encrypted stuff!  
 * Switched from PEM+base64 to DER+base64!  
 * Made another migrate script, not going to upload it because nobody needs it anyway...  
* 08/27/2017 v1.0.0 (id01)  
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
* sjcl library (BSD License)  
* jQuery (MIT license)  
* Python, WebExtensions, Javascript, PHP, HTML, C, Shell and every other programming language I used :)
 Also, special thanks to my PC, router, Raspberry Pi, and web browser for making this possible :D Lol
Note: Licenses for software used can be found in licenses/

## Dependencies
* Python 2.x  
* Python cryptography library  
* Mysql (server only)  
* secure-delete (server only)  
* An http server (server only)  
