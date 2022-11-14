#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    @author:  codeuk
    @package: core/other/tools.py
"""

import time
import socket

from threading import active_count, Thread

from core.other.output import *

def start_threads(func: callable, threads: int=3, args: tuple=()) -> None:
    """starts specific threads on a supplied function

    :param callable func: function to start threading on
    :param str threads: amount of times to loop threading
    :return: None
    """

    for _ in range(threads):
        thread = Thread(target=func, args=args)
        thread.start()

def ping(host: str="127.0.0.1", port: int=80, timeout: int=2) -> None:
    """ping supplied api on a specific port

    :param str host: api ip to ping
    :param int port: specific port to ping on
    :param int timeout: timeout to supply socket.timeout
    :return: None
    """

    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        sock.connect((host,port))
    except Exception as e:
        warn("Tantalus has failed to make a connection to {}\n".format(host))
    else:
        sock.close()
        plus("Tantalus Web API is up!\n")

def get_inp(txt: str=f"{E}{W}[tantalus]{E} $ {W}") -> str:
    """simple input function to omit blank queries

    :param str txt: text to use for input
    :return: user input
    :rtype: str
    """

    inp = input(txt)
    while inp == "":
        inp = input(txt)

    return inp

def get_time() -> str:
    """get the current system time in utc"""

    time_unfiltered = time.gmtime(time.time())
    formatted_time = time.strftime("%Y-%m-%d %H:%M:%S", time_unfiltered)
    return formatted_time + " UTC"