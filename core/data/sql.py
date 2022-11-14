#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author:  codeuk
    @package: core/data/sql.py
"""

import re
import sqlite3

from typing import Union

from core.other.config import *
from core.other.output import *
from core.other.tools import get_time


class SQL(Encryption):
    """Tantalus SQLite3 Database Tools"""

    def __init__(self):
        Encryption.__init__(self)
        self.connection = connection = self.connect_db()
        self.cursor = connection.cursor()
        self.make_tables()
        self.connection.commit()

    @staticmethod
    def connect_db(path: str="database/database.db") -> sqlite3.Connection:
        """creates and connects to the sqlite3 database

        :param str path: Path to store/create the database
        :return: sqlite3 database connection
        :rtype: sqlite3.Connection
        """

        conn = sqlite3.connect(path, check_same_thread=False)
        return conn

    def make_tables(self):
        """creates the tables using SQL scripts from core.other.config"""

        try:
            self.cursor.execute(SQL_ACCOUNT_TABLE)
            self.cursor.execute(SQL_CONNECTION_TABLE)
        except Exception as e:
            warn("Tantalus has encountered an exception while creating database tables: {}".format(e))

    def fetch_user(self, username: str, password: str) -> Union[list, bool]:
        """fetch one account from the accounts database from the username

        :param str username: account username
        :param str password: account password
        :return: user account if found else None
        :rtype: Union[list, bool]
        """

        self.cursor.execute(
            'SELECT * FROM accounts WHERE username = (?)', (username,))
        account = self.cursor.fetchone()

        if account != None:
            password_hash = account[2]
            decrypted = self.decrypt(password_hash.encode(), password)

            if decrypted == password:
                return account

        return False

    def change_user_password(self, username: str, password: str, new_password: str) -> list[str, bool]:
        """update user password from username

        :param str username: account username to change password for
        :param str password: account password to validate
        :param str new_password: new account password
        :return: alert message for frontend panel, bool if pass changed
        :rtype: list[str, bool]
        """

        account = self.fetch_user(username, password)
        if account != False and 4 <= len(new_password) <= 35:
            self.cursor.execute(
                'UPDATE accounts SET password = (?) WHERE id=?',(new_password, account[0]))
            self.connection.commit()
            return "Worked: Password has been changed successfully!", True

        return "Failed: Password could not be changed", False

    def register_user(self, username: str, password: str, admin: bool=False) -> bool:
        """register user account to database using User dataclass

        :param str username: accounts username
        :param str password: accounts password
        :return: bool user account if found or created
        :rtype: bool
        """

        self.cursor.execute(
            f'SELECT * FROM accounts WHERE username = (?)', (username,))
        account = self.cursor.fetchone()

        if account:
            return False
        elif not re.match(r'[A-Za-z0-9]+', username):
            return False
        else:
            app_secret = Secrets.generate_secret(50)
            self.cursor.execute('INSERT INTO accounts VALUES (NULL, (?), (?), (?), (?))',
                                (username, password, admin, app_secret))
            self.connection.commit()
            return True

    def get_accounts(self) -> Union[list, None]:
        """get all user accounts

        :return: list all account details in the database
        :rtype: Union[list, None]
        """

        self.cursor.execute('SELECT * FROM accounts')
        accounts = self.cursor.fetchall()
        return accounts

    def get_user_account(self, username: str) -> Union[list, None]:
        """get user account from username

        :param str username: username of account to return
        :return: account details of specified user or None if not found
        :rtype: Union[list, None]
        """

        self.cursor.execute(
            'SELECT * FROM accounts WHERE username = (?)', (username,))
        account = self.cursor.fetchone()
        return account

    def remove_account(self, username: int):
        """remove account from username

        :param str username: username of account to remove
        :return: None
        """

        self.cursor.execute(
            'DELETE FROM accounts WHERE username=(?)', (username,))
        self.connection.commit()

    def clear_db(self, my_user: str):
        """delete all accounts in the database except the current user

        :param str my_user: username of sole account not to remove
        :return: None
        """

        self.cursor.execute(
            'DELETE FROM accounts WHERE username <> (?)', (my_user,))
        self.connection.commit()

    def refresh_secret(self, id: int) -> bool:
        """iterate and find user by id then refresh client secret

        :param int id: id of account
        :return: if secret was updated successfully
        :rtype: bool
        """
        new_app_secret = Secrets.generate_secret(50)
        self.cursor.execute(
            'UPDATE accounts SET secret = (?) WHERE id=?', (new_app_secret, id))
        self.connection.commit()
        return True

    def add_connection(self, id: int, username: str, ip: str, port: int, os: str, connected: str) -> bool:
        """add a bot connection to the connections database

        :param str id: bots session id
        :param str username: bots pc username
        :param str password: bots ip
        :param str connected: time in utc that connection was initiated
        :return: true or false based on if the connection is a duplicate
        :rtype: boolean
        """

        self.cursor.execute(f'SELECT * FROM connections WHERE id = (?)', (id,))
        connection = self.cursor.fetchone()

        if connection:
            return False
        else:
            self.cursor.execute('INSERT INTO connections VALUES (NULL, (?), (?), (?), (?), (?))',
                                (username, ip, port, os, connected))
            self.connection.commit()
            return True

    def get_connections(self) -> Union[list, None]:
        """get all bot connections

        :return: list all bot details in the database or None
        :rtype: Union[list, None]
        """

        self.cursor.execute('SELECT * FROM connections')
        bots = self.cursor.fetchall()
        return bots