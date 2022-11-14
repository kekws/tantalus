#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author:  codeuk
    @package: core/security/secrets.py
"""

import secrets


class Secrets:

    @staticmethod
    def generate_secret(len: int=20) -> str:
        """generate an application secret

        :param str len: length of secret to generate, default: 20
        :return: application secret
        :rtype: str
        """

        application_secret = secrets.token_hex(len)
        return application_secret