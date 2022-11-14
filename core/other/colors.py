#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author:  codeuk
    @package: core/other/colors.py
"""

from colorama import Fore, init
init()

R = Fore.RED # "\033[%s;31m"
B = Fore.BLUE # "\033[%s;34m"
G = Fore.GREEN # "\033[%s;32m"
W = Fore.WHITE # "\033[%s;38m"
Y = Fore.YELLOW # "\033[%s;33m"
M = Fore.MAGENTA # idk
E = Fore.RESET # "\033[0m"