import sys;
import SocketServer;
import socket;
import subprocess;

class RequestHandler(SocketServer.BaseRequestHandler):
	def handle(self):
		conn = self.request;
		conn.settimeout(0.5);
		print self.client_address[0] + " connected.";
		data = conn.recv(4096);
		if data:
			sub = subprocess.Popen(["python", "passwords.py"], stdout=subprocess.PIPE, stdin=subprocess.PIPE);
			conn.send(sub.communicate(input=data)[0]);
		conn.shutdown(socket.SHUT_RDWR);
		conn.close();

sserver = SocketServer.TCPServer(('0.0.0.0', 3000), RequestHandler);
sserver.serve_forever();
