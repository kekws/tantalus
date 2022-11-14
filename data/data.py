#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author:  codeuk
    @package: core/data/data.py
"""

from dataclasses import dataclass

from core.data.sql import *
from core.security.secrets import *


class Dataclass(SQL):
    """Data Related Functions"""

    def __init__(data):
        SQL.__init__(data)
        data.session_bots = []
        data.session_users = []

    @dataclass
    class Bot:
        """bot connection dataclass

        :param int id: primary key
		:param str ip: ip address
        :param int port: port connected from
        :param str username: bot pc username
        :param str os: operating system
        :param str connected: time (utc) bot connected
		:return: bot object
		:rtype: object
        """

        id: int
        username: str
        ip: str
        port: int
        os: str
        connected: str

    @dataclass
    class User:
        """user account dataclass

        :param int id: primary key
		:param str username: account username
        :param str password: account password
        :param bool admin: access level
        :param str secret: application secret
		:return: user object
		:rtype: object
        """

        id: int
        username: str
        password: str
        admin: bool = False
        secret: str = Secrets.generate_secret()

    def add_user(data, username: str, password: str, admin: bool=False) -> list[bool, str]:
        """store data in the session_users and accounts database using the User dataclass

		:param str username: account username
        :param str password: account password
        :param bool admin: access level
		:return: bool if validated, success or error
		:rtype: list[bool, str]
        """

        new_user = data.User(id=len(data.session_users)+1, username=username,
                             password=password, admin=admin)

        if data.register_user(username, password, admin):
            data.session_users.append(new_user)
            return True, "user added"
        else:
            return False, "register error"

    def validate_user(data, username: str, password: str, admin: bool=False) -> list[bool, str]:
        """check if a supplied username and password are fit for use

		:param str username: account username
        :param str password: account password
        :param bool admin: access level
		:return: bool if user validated, error message
		:rtype: list[bool, str] or bool
		"""

        if len(username) < 3:
            return False, "user length too short"
        elif len(username) > 20:
            return False, "user length too long"

        if len(password) < 4:
            return False, "password length too short"
        elif len(password) > 150:
            return False, "password length too long"

        for user in data.session_users:
            if user.username == username:
                return False, "username is already in use"

        password_hash = Encryption.encrypt(data=password, password=password)
        return data.add_user(username, password_hash, admin)

    def compare_logins(data, username: str, password: str) -> list[bool, bool]:
        """compare logins using SQL.fetch_user(username, password)

		:param str username: account username to match
        :param str password: account password to match
		:return: user exists bool, admin access bool
		:rtype: list[bool, bool]
        """

        account = data.fetch_user(username, password)
        if account != False:
            admin = account[3]
            return True, True if admin=='1' else False


        return False, False