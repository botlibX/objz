# This file is placed in the Public Domain.


"utilities"


import importlib
import importlib.util
import logging
import os
import sys
import threading
import time


import _thread


LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


class Event:

    def __init__(self):
        self.ctime = time.time()
        self.result = {}
        self.type = "event"

    def display(self):
        for tme in sorted(self.result):
            self.dosay(
                       self.result[tme]
                      )

    def dosay(self, txt):
        raise NotImplementedError("dosay")

    def reply(self, txt):
        self.result[time.time()] = txt


class Formatter(logging.Formatter):

    def format(self, record):
        record.module = record.module.upper()
        return logging.Formatter.format(self, record)


def elapsed(seconds, short=True):
    txt = ""
    nsec = float(seconds)
    if nsec < 1:
        return f"{nsec:.2f}s"
    yea     = 365 * 24 * 60 * 60
    week    = 7 * 24 * 60 * 60
    nday    = 24 * 60 * 60
    hour    = 60 * 60
    minute  = 60
    yeas    = int(nsec / yea)
    nsec   -= yeas * yea
    weeks   = int(nsec / week)
    nsec   -= weeks * week
    nrdays  = int(nsec / nday)
    nsec   -= nrdays * nday
    hours   = int(nsec / hour)
    nsec   -= hours * hour
    minutes = int(nsec / minute)
    nsec   -= int(minute * minutes)
    sec     = int(nsec)
    if yeas:
        txt += f"{yeas}y"
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += f"{nrdays}d"
    if short and txt:
        return txt.strip()
    if hours:
        txt += f"{hours}h"
    if minutes:
        txt += f"{minutes}m"
    if sec:
        txt += f"{sec}s"
    txt = txt.strip()
    return txt


def forever():
    while True:
        try:
            time.sleep(0.1)
        except (KeyboardInterrupt, EOFError):
            break


def importer(name, pth):
    if not os.path.exists(pth):
        return
    try:
        spec = importlib.util.spec_from_file_location(name, pth)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        if not mod:
            return
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        logging.info("load %s", pth)
        return mod
    except Exception as ex:
        logging.exception(ex)
        _thread.interrupt_main()


def launch(func, *args, **kwargs):
    thread = threading.Thread(None, func, name(func), tuple(args), dict(kwargs), daemon=True)
    thread.start()
    return thread


def level(loglevel="debug"):
    if loglevel != "none":
        datefmt = "%H:%M:%S"
        format_short = "%(module).3s %(message)-76s"
        ch = logging.StreamHandler()
        ch.setLevel(LEVELS.get(loglevel))
        formatter = Formatter(fmt=format_short, datefmt=datefmt)
        ch.setFormatter(formatter)
        logger = logging.getLogger()
        logger.addHandler(ch)


def name(obj, short=False):
    typ = type(obj)
    res = ""
    if "__builtins__" in dir(typ):
        res = obj.__name__
    elif "__self__" in dir(obj):
        res = f"{obj.__self__.__class__.__name__}.{obj.__name__}"
    elif "__class__" in dir(obj) and "__name__" in dir(obj):
        res = f"{obj.__class__.__name__}.{obj.__name__}"
    elif "__class__" in dir(obj):
        res =  f"{obj.__class__.__module__}.{obj.__class__.__name__}"
    elif "__name__" in dir(obj):
        res = f"{obj.__class__.__name__}.{obj.__name__}"
    if short:
        res = res.split(".")[-1]
    return res


def __dir__():
    return (
       'elapsed',
       'forever',
       'launch',
       'level',
       'name'
    )
