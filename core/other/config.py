#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author:  codeuk
    @package: core/other/info.py
"""

from requests import get

from core.security.secrets    import *
from core.security.encryption import *

VERSION = 0.1
AUTHOR = "codeuk"
GITHUB = "github.com/codeuk"

API_URL = "http://127.0.0.1"
API_NAME = "Tantalus Web Panel"
API_PORT = 80
API_DEBUG = True
API_SECRET_KEY = Secrets.generate_secret(20)
GOOGLE_API_KEY = ""
SERVER_IP = get('https://api.ipify.org').content.decode('utf8')
DEFAULTS =["127.0.0.1", "5000", API_SECRET_KEY, SERVER_IP]

SQL_ACCOUNT_TABLE = """
CREATE TABLE IF NOT EXISTS `accounts` (
    `id` integer PRIMARY KEY,
    `username` varchar(50) NOT NULL,
    `password` varchar(255) NOT NULL,
    `admin` varchar(100) NOT NULL,
    `secret` varchar(255) NOT NULL
); """

SQL_CONNECTION_TABLE = """
CREATE TABLE IF NOT EXISTS `connections` (
    `id` integer PRIMARY KEY,
    `username` varchar(50) NOT NULL,
    `ip` varchar(25) NOT NULL,
    `port` integer NOT NULL,
    `os` varchar(10) NOT NULL,
    `connected` varchar(50) NOT NULL
);
"""