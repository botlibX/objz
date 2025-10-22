# This file is placed in the Public Domain.


import inspect
import time


from .package import getmod, modules


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
        self.args = []
        self.gets = {}
        self.orig = ""
        self.rest = ""
        self.result = {}
        self.sets = {}
        self.txt = ""
        self.type = "event"

    def display(self):
        for tme in sorted(self.result):
            print(self.result[tme])

    def parse(self, txt):
        self.otxt = txt or self.txt
        self.cmd = self.otxt and self.otxt.split()[0]
        self.args = self.cmd and self.otxt.split()[1:]
        self.rest = self.args and  " ".join(self.args)
        self.txt = self.args and " ".join(self.args)

    def reply(self, txt):
        self.result[time.time()] = txt


def command(evt):
    evt.parse(evt.txt)
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


def __dir__():
    return (
        'Commands',
        'Event',
        'command',
        'scan',
        'scanner'
    )
