#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author:  codeuk
    @package: core/security/encryption.py
"""

import secrets

from os import urandom
from random import randint
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from base64 import urlsafe_b64encode as b64e, urlsafe_b64decode as b64d


class Encryption:
    """Tantalus Encryption by Jonah / @nopjo"""

    @staticmethod
    def random_index() -> str:
        """generate the 1st random hex string

        :return: random hex string
        :rtype: str
        """

        return str(urandom(randint(5,15)).hex())

    @staticmethod
    def secret_key() -> str:
        """generate the 2nd random hex string

        :return: random hex string
        :rtype: str
        """

        return str(urandom(randint(15,25)).hex())

    @staticmethod
    def _derive_key(password: bytes, salt: bytes, iterations: int = 100_000) -> bytes:
        """generate a key from the supplied salt

        :param bytes password: password to hash
        :param bytes salt: salt to hash the password with
        :param int iterations: how many times to hash the password
        :return: pbkf2hmac key
        :rtype: bytes
        """

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(), length=32, salt=salt,
            iterations=iterations, backend=default_backend())
        return b64e(kdf.derive(password))

    @staticmethod
    def encrypt(data: str, password: str, iterations: int = 100_000) -> str:
        """encrypt the data using the salt derived from the password

        :param bytes password: password to hash
        :param bytes salt: salt to hash the password with
        :param int iterations: how many times to hash the password
        :return: pbkf2hmac key
        :rtype: str
        """

        salt = secrets.token_bytes(16)
        key = Encryption._derive_key(password.encode(), salt, iterations)
        return b64e(
            b'%b%b%b' % (
                salt,
                iterations.to_bytes(4, 'big'),
                b64d(Fernet(key).encrypt(data.encode())),
            )
        ).decode()

    @staticmethod
    def decrypt(token: bytes, password: str) -> bytes:
        """decrypt token hash using password

        :param bytes token: tantalus encrypted hash
        :param bytes password: salt to hash the password with
        :return: decrypted key
        :rtype: bytes
        """

        decoded = b64d(token)
        salt, iter, token = decoded[:16], decoded[16:20], b64e(decoded[20:])
        iterations = int.from_bytes(iter, 'big')
        key = Encryption._derive_key(password.encode(), salt, iterations)
        try:
            decrypted = Fernet(key).decrypt(token).decode()
        except Exception as InvalidTokenError:
            decrypted = None
        finally:
            return decrypted