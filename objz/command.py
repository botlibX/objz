# This file is placed in the Public Domain.


"modules"


import inspect
import os
import sys
import threading
import time


from objz.methods import parse
from objz.utility import importer


d = os.path.dirname


class Config:

    debug = False
    default = ""
    init  = ""
    level = "warn"
    name = d(d(__file__)).split(os.sep)[-1]
    verbose = False
    version = 102


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


def scanner(names=[]):
    res = []
    for nme in modules():
        if names and nme not in names:
            continue
        module = getmod(nme)
        if not module:
            continue
        scan(module)
        res.append(module)
    return res


class Mods:

    debug = False
    dirs = {}
    md5s = {}

    @staticmethod
    def dir(name, path):
        Mods.dirs[name] = path


def getmod(name):
    for nme, path in Mods.dirs.items():
        mname = nme + "." +  name
        module = sys.modules.get(mname, None)
        if module:
            return module
        pth = os.path.join(path, f"{name}.py")
        mod = importer(mname, pth)
        if mod:
            return mod


def inits(names):
    modz = []
    for name in modules():
        if name not in names:
            continue
        try:
            module = getmod(name)
            if module and "init" in dir(module):
                thr = launch(module.init)
                modz.append((module, thr))
        except Exception as ex:
            logging.exception(ex)
            _thread.interrupt_main()
    return modz


def modules():
    mods = []
    for name, path in Mods.dirs.items():
        if not os.path.exists(path):
            continue
        mods.extend([
            x[:-3] for x in os.listdir(path)
            if x.endswith(".py") and not x.startswith("__")
           ])
    return sorted(mods)



def __dir__():
    return (
        'Commands',
        'Config',
        'Event',
        'Mods',
        'command',
        'getmod',
        'importer',
        'inits',
        'md5sum',
        'modules',
        'scan'
    )
