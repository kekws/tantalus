#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author:  codeuk
    @package: core/security/login.py
"""

from core.data.data import *
from core.other.tools  import *
from core.security.encryption import *


class Login(Dataclass, Encryption):

    def __init__(self):
        Dataclass.__init__(self)
        Encryption.__init__(self)
        self.account  = None
        self.username = None
        self.password = None
        self.is_admin = False
        self.default_users()

    def default_users(self):
        """add default set of users to the database and session_users"""

        self.validate_user(username="admin", password="root", admin=True)
        self.validate_user(username="user",  password="root", admin=False)