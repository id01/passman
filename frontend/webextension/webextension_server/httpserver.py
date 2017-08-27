import socket;
import SocketServer;
import urllib;
import communicator;

magicString = "PASSMAN+INPUT+IS=" # String to look for

def sendHTTPResult(conn, toSend):
	conn.send("HTTP/1.1 200 OK\n");
	conn.send("Server: SocketServer\n");
	conn.send("Content-Type: text/text\n");
	conn.send("Content-Length: "+str(len(toSend))+"\n");
	conn.send("Connection: close\n\n");
	conn.send(toSend);

class RequestHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		conn = self.request;
		conn.settimeout(3.0);
		print "Client Connected.";
		closedConnection = False;
		data = conn.recv(4096).split('\n');
		if not data:
			conn.shutdown(socket.SHUT_RDWR);
			conn.close();
			closedConnection = True;
		else:
			for line in data:
				if line[:len(magicString)] == magicString:
					myLine = urllib.unquote(line[len(magicString):]).split('\n');
					for i in range(len(myLine)):
						myLine[i] = myLine[i].strip('\r');
					try:
						myResult = communicator.communicate(myLine[0], myLine[1], myLine[2].replace('+', ' '));
						sendHTTPResult(conn, myResult);
					except (ValueError, IndexError) as e:
						print e;
						conn.send("Malformed Input.\n");
					conn.shutdown(socket.SHUT_RDWR);
					conn.close();
					closedConnection = True;

sserver = SocketServer.TCPServer(('127.0.0.1', 13880), RequestHandler);
sserver.serve_forever();
