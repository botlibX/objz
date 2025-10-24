# This file is placed in the Public Domain.


"modules"


import inspect
import os
import sys
import threading
import time


from objz.utility import importer


d = os.path.dirname
lock = threading.RLock()


class Config:

    debug = False
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


class Mods:

    debug = False
    dirs = {}

    @staticmethod
    def dir(name, path):
        Mods.dirs[name] = path


def command(evt):
    parse(evt, evt.txt)
    func = Commands.get(evt.cmd)
    if func:
        func(evt)
        evt.display()


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


def modules():
    mods = []
    for _name, path in Mods.dirs.items():
        if not os.path.exists(path):
            continue
        mods.extend([
            x[:-3] for x in os.listdir(path)
            if x.endswith(".py") and not x.startswith("__")
           ])
    return sorted(mods)


def parse(obj, txt=""):
    if not txt:
        if "txt" in dir(obj):
            txt = obj.txt
    args = []
    setattr(obj, "args", getattr(obj, "args", []))
    setattr(obj, "cmd" , getattr(obj, "cmd", ""))
    setattr(obj, "gets", getattr(obj, "gets", {}))
    setattr(obj, "index", getattr(obj, "index", None))
    setattr(obj, "inits", getattr(obj, "inits", ""))
    setattr(obj, "mod" ,  getattr(obj, "mod", ""))
    setattr(obj, "opts", getattr(obj, "opts", ""))
    setattr(obj, "rest", getattr(obj, "rest", ""))
    setattr(obj, "result", getattr(obj, "result", ""))
    setattr(obj, "sets", getattr(obj, "sets", {}))
    setattr(obj, "silent", getattr(obj, "silent", {}))
    setattr(obj, "txt", txt or getattr(obj, "txt", ""))
    setattr(obj, "otxt", obj.txt or getattr(obj, "otxt", ""))
    _nr = -1
    for spli in obj.otxt.split():
        if spli.startswith("-"):
            try:
                obj.index = int(spli[1:])
            except ValueError:
                obj.opts += spli[1:]
            continue
        if "-=" in spli:
            key, value = spli.split("-=", maxsplit=1)
            obj.silent[key] = value
            obj.gets[key] = value
            continue
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            obj.gets[key] = value
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            obj.sets[key] = value
            continue
        _nr += 1
        if _nr == 0:
            obj.cmd = spli
            continue
        args.append(spli)
    if args:
        obj.args = args
        obj.txt  = obj.cmd or ""
        obj.rest = " ".join(obj.args)
        obj.txt  = obj.cmd + " " + obj.rest
    else:
        obj.txt = obj.cmd or ""


def scan(module):
    for key, cmdz in inspect.getmembers(module, inspect.isfunction):
        if key.startswith("cb"):
            continue
        if 'event' in inspect.signature(cmdz).parameters:
            Commands.add(cmdz)


def scanner(names=[]):
    res = []
    for nme in sorted(modules()):
        if names and nme not in names:
            continue
        module = getmod(nme)
        if not module:
            continue
        scan(module)
        res.append(module)
    return res


def __dir__():
    return (
        'Commands',
        'Event',
        'Mods',
        'command',
        'getmod',
        'modules',
        'p'
        'scan',
        'scanner'
    )
