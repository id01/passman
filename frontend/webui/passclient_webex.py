import sys, json, struct, os;

def getMessage():
	rawLength = sys.stdin.read(4);
	if len(rawLength) == 0:
		sys.exit(0);
	messageLength = struct.unpack("@I", rawLength)[0]
	message = sys.stdin.read(messageLength);
	return json.loads(message).get("text");

def encodeMessage(content):
	encodedContent = json.dumps(content);
	encodedLength = struct.pack("@I", len(encodedContent));
	return {'length': encodedLength, 'content': encodedContent};

def sendMessage(encodedMessage):
	sys.stdout.write(encodedMessage['length'])
	sys.stdout.write(encodedMessage['content'])
	sys.stdout.flush()

# For some reason, this doesn't work unless written to file
recievedMessage = getMessage()
a = open("/tmp/passman.passwd", "w")
a.close()
os.chmod("/tmp/passman.passwd", 0600);
a = open("/tmp/passman.passwd", "w")
a.write(recievedMessage);
a.close();
x = os.popen("python passclient_webui.py </tmp/passman.passwd 2>/tmp/passman.log").read();
os.unlink("/tmp/passman.passwd");
sendMessage(encodeMessage(x));
