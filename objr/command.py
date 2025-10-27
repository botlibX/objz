# This file is placed in the Public Domain.


"write your own commands"


import inspect
import os


from objr.brokers import Fleet
from objr.package import getmod, modules


class Config:

    debug = False
    init  = "irc,rss"
    level = "warn"
    name = os.path.dirname(__file__).split(os.sep)[-1]
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


def command(evt):
    parse(evt, evt.txt)
    func = Commands.get(evt.cmd)
    if func:
        func(evt)
        Fleet.display(evt)
    evt.ready()


def parse(obj, txt):
    data = {
        "args": [],
        "cmd": "",
        "gets": {},
        "index": None,
        "init": "",
        "opts": "",
        "otxt": txt,
        "rest": "",
        "silent": {},
        "sets": {},
        "txt": ""
    }
    for k, v in data.items():
        setattr(obj, k, getattr(obj, k, v))
    args = []
    nr = -1
    for spli in txt.split():
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
        nr += 1
        if nr == 0:
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
    for nme in modules():
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
        'Comamnds',
        'Config',
        'command',
        'parse',
        'scan',
        'scanner'
    )
