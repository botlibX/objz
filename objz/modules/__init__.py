# This file is placed in the Public Domain.


"modules"


import importlib.util
import inspect
import logging
import os
import sys
import threading
import time
import _thread


from objz.methods import name


d = os.path.dirname
lock = threading.RLock()


"config"


class Config:

    debug = False
    init  = ""
    level = "warn"
    name = d(d(__file__)).split(os.sep)[-1]
    verbose = False
    version = 102


"threads"


def forever():
    while True:
        try:
            time.sleep(0.1)
        except (KeyboardInterrupt, EOFError):
            break


def launch(func, *args, **kwargs):
    thread = threading.Thread(None, func, name(func), tuple(args), dict(kwargs), daemon=True)
    thread.start()
    return thread


"commands"


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


"modules"


class Mods:

    debug = False
    dirs = {}

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


def inits(names):
    modz = []
    for nme in modules():
        if nme not in names:
            continue
        try:
            module = getmod(nme)
            if module and "init" in dir(module):
                thr = launch(module.init)
                modz.append((module, thr))
        except Exception as ex:
            logging.exception(ex)
            _thread.interrupt_main()
    return modz


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


"utilities"


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


def __dir__():
    return (
        'Commands',
        'Mods',
        'command',
        'elapsed',
        'getmod',
        'modules',
        'inits',
        'parse',
        'scan',
        'scanner'
    )
