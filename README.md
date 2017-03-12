## Password Manager
Note: I haven't come up with a good name yet.  
Another note: This only works on Linux as of the moment. However, it shouldn't be too hard to port the client.  
This is a (somewhat) simple password manager that runs on mySQL.  

## Backend Installation
Install mysql, gcc, pyelliptic.  
Run ./setup.sh  
Run ./service.sh to start the service.  
Symlink a folder on your webserver to this folder for setting up of new users from the internet.  

## Frontend Installation
Install web extension on browser. It won't work yet.  
Run ./install.sh in the frontend/webui folder. MAKE SURE TO RUN IT IN THE RIGHT FOLDER!!!  
Change "host" and "port" parameters in frontend/webui/passclient_webui.py file to appropriate values so you can connect to the right server.  

## Features
Variable symmetric and elliptic curve algorithms. (Including AES-256 and sect571k1)  
Master Key and passwords never transmitted over internet except initial registration over webUI.  
Server has zero knowledge of any passwords or master key, except initial registration over webUI.  
Passwords stored on server encrypted with AES and generated at client side after secure elliptic-curve handshake.  
Centralized password management without need for copying any files.  

## Other Notes
ALWAYS run the registration web server over SSL. Otherwise, the world (and all your passwords) will be destroyed. But seriously. Don't run the webserver over plaintext. It's not good for your health.  
ALWAYS remember to install all dependencies, or else bad things will happen.  

## Todo
Allow webUI to fetch passwords and decrypt them on the client side.  
Don't write to disk, even though file is zeroed out using filenuke.c.  
Switch to a different, better-maintained cryptography library that is more standard and also supports Elliptic Curve.  

## Changelog
* xx/xx/xxxx (id01)  
 * Switched AES/SHA/MD5 library back to pyCrypto  
* 03/27/2017 (id01)  
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
* 02/28/2017 (id01)  
 * Start of project.  

## Credits
* PyElliptic library by yann2192
* PyCrypto library
* Python, WebExtensions, Javascript, PHP, HTML, C, Shell and every other programming language I used :)