from __future__ import print_function

import os
import time
import traceback
import logging


class AnsiEscape:
    """
    Black        0;30     Dark Gray     1;30
    Red          0;31     Light Red     1;31
    Green        0;32     Light Green   1;32
    Brown/Orange 0;33     Yellow        1;33
    Blue         0;34     Light Blue    1;34
    Purple       0;35     Light Purple  1;35
    Cyan         0;36     Light Cyan    1;36
    Light Gray   0;37     White         1;37
    """
    RED = '\033[0;31m'
    YELLOW = '\033[0;33m'
    LIGHTGRAY = '\033[0;37m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'

    HEADER = '\033[95m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    NOCOLOR = '\033[0m'


def _get_prefix():
    trcb = traceback.extract_stack()
    assert len(trcb) > 2
    currtime = time.strftime("%H:%M:%S")
    filename = os.path.basename(trcb[-3][0])
    assert filename != os.path.basename(__file__)
    funcname = trcb[-3][2]
    prefix = "{}/{}/{}".format(currtime, filename, funcname)
    return "{0:{1}}".format(prefix, 20)


def notice(msg=""):
    color = AnsiEscape.YELLOW
    msg_with_prefix = "{} {}".format(_get_prefix(), msg)
    logging.info("{}{}{}".format(color, msg_with_prefix, AnsiEscape.NOCOLOR))


def info(msg=""):
    color = AnsiEscape.NOCOLOR
    msg_with_prefix = "{} {}".format(_get_prefix(), msg)
    logging.info("{}{}{}".format(color, msg_with_prefix, AnsiEscape.NOCOLOR))


def detail(msg=""):
    color = AnsiEscape.LIGHTGRAY
    msg_with_prefix = "{} {}".format(_get_prefix(), msg)
    logging.info("{}{}{}".format(color, msg_with_prefix, AnsiEscape.NOCOLOR))


def warn(msg=""):
    color = AnsiEscape.WARNING
    msg_with_prefix = "{} {}".format(_get_prefix(), msg)
    logging.warning("{}{}{}".format(color, msg_with_prefix, AnsiEscape.NOCOLOR))


def error(msg=""):
    color = AnsiEscape.RED
    msg_with_prefix = "{} {}".format(_get_prefix(), msg)
    logging.error("{}{}{}".format(color, msg_with_prefix, AnsiEscape.NOCOLOR))
