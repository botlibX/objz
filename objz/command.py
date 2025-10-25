# This file is placed in the Public Domain.


"modules"


import inspect
import os
import sys
import threading
import time


from objz.methods import parse
from objz.utility import getmod, modules


d = os.path.dirname


class Config:

    debug = False
    default = ""
    init  = ""
    level = "warn"
    name = d(d(__file__)).split(os.sep)[-1]
    verbose = False
    version = 102


class Commands:

    cmds = {}
    names = {}

    @staticmethod
    def add(func) -> None:
        name = func.__name__
        Commands.cmds[name] = func
        Commands.names[name] = func.__module__

    @staticmethod
    def get(cmd):
        return Commands.cmds.get(cmd, None)


class Event:

    def __init__(self):
        self._ready = threading.Event()
        self.ctime = time.time()
        self.result = {}
        self.type = "event"

    def display(self):
        for tme in sorted(self.result):
            self.dosay(
                       self.result[tme]
                      )
        self.ready()

    def dosay(self, txt):
        raise NotImplementedError("dosay")

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        self.result[time.time()] = txt

    def wait(self):
        self._ready.wait()


def command(evt):
    parse(evt, evt.txt)
    func = Commands.get(evt.cmd)
    if func:
        func(evt)
        evt.display()
    evt.ready()


def scan(module):
    for key, cmdz in inspect.getmembers(module, inspect.isfunction):
        if key.startswith("cb"):
            continue
        if 'event' in inspect.signature(cmdz).parameters:
            Commands.add(cmdz)


def scanner(path, modname="", names=[]):
    res = []
    for nme in modules(path):
        if names and nme not in names:
            continue
        module = getmod(path, modname, nme)
        if not module:
            continue
        scan(module)
        res.append(module)
    return res


def __dir__():
    return (
        'Commands',
        'Event',
        'command',
        'scan'
    )
