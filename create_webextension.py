import os;
from os import mkdir;

def cp(inf, outf):
	with open(inf, 'r') as inFile:
		with open(outf, 'w') as outFile:
			outFile.write(inFile.read());

def www2ext(filePath):
	cp(WWWROOT+'/'+filePath, EXTROOT+'/'+filePath);

WWWROOT = "backend/wwwroot";
EXTROOT = "webextension/wwwroot";
URLLOCATION = raw_input("Enter URL Location of this directory: ").rstrip('/')+'/';
if URLLOCATION == "":
	print "Aborted";
	exit(1);
mkdir("webextension");
mkdir("webextension/wwwroot");
mkdir(EXTROOT+"/bootstrap");
mkdir(EXTROOT+"/javascript");
www2ext("bootstrap/bootstrap.js");
www2ext("javascript/addpass2.min.js");
www2ext("javascript/getpass2.min.js");
with open(EXTROOT+"/javascript/global.min.js", 'w') as globalFile:
	globalFile.write('var urllocation = "'+URLLOCATION+'";');
	with open(WWWROOT+"/javascript/global.js", 'r') as globalFileWWW:
		globalFile.write('\n'.join(globalFileWWW.read().split('\n')[1:]));
www2ext("getpass.html");
www2ext("addpass.html");
os.system("cp webextension_template/* webextension/");
with open("webextension/manifest.json", 'r') as manifestFile:
	manifestFileContent = manifestFile.read().replace('_URLLOCATION_', '"'+URLLOCATION+'"');
with open("webextension/manifest.json", 'w') as manifestFile:
	manifestFile.write(manifestFileContent);