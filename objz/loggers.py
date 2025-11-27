# This file is placed in the Public Domain.


import logging
import time


from .configs import Config 
from .statics import LEVELS
from .utility import getdir


class Logging:

    datefmt = "%H:%M:%S"
    format = "%(module).3s %(message)s"


class Format(logging.Formatter):

    def format(self, record):
        record.module = record.module.upper()
        return logging.Formatter.format(self, record)


def banner():
    tme = time.ctime(time.time()).replace("  ", " ")
    logger = logging.getLogger()
    logging.warn("%s %s since %s (%s)" % (
                                   Config.name.upper(),
                                   Config.version,
                                   tme,
                                   logging.getLevelName(logger.getEffectiveLevel())
                                  ))


def level(loglevel="debug"):
    lvl = LEVELS.get(loglevel)
    if not lvl:
        return
    logger = logging.getLogger()
    for handler in logger.handlers:
        logger.removeHandler(handler)
    logger.setLevel(lvl)
    formatter = Format(Logging.format, datefmt=Logging.datefmt)
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)


__dir__ = getdir('Logging', 'banner', 'level')
