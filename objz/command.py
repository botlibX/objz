# This file is placed in the Public Domain.


"modules"


import inspect
import logging
import os
import sys
import threading
import time
import _thread


from objz.methods import fmt, name
from objz.utility import importer, launch, parse


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
        self._ready = threading.Event()
        self._thr = None
        self.args = []
        self.channel = ""
        self.ctime = time.time()
        self.orig = ""
        self.rest = ""
        self.result = {}
        self.txt = ""
        self.type = "event"

    def display(self):
        for tme in sorted(self.result):
            self.dosay(
                       self.channel,
                       self.result[tme]
                      )

    def dosay(self, channel, txt):
        print(txt)

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        self.result[time.time()] = txt

    def wait(self, timeout=None):
        try:
            self._ready.wait()
            if self._thr:
                self._thr.join(timeout)
        except (KeyboardInterrupt, EOFError):
            _thread.interrupt_main()


class Handler:

    def __init__(self):
        self.cbs = {}
        self.queue = queue.Queue()

    def callback(self, event):
        func = self.cbs.get(event.type, None)
        if func:
            name = event.txt and event.txt.split()[0]
            event._thr = launch(func, event, name=name)
        else:
            event.ready()

    def loop(self):
        while True:
            try:
                event = self.poll()
                if event is None:
                    break
                event.orig = repr(self)
                self.callback(event)
            except (KeyboardInterrupt, EOFError):
                _thread.interrupt_main()

    def poll(self):
        return self.queue.get()

    def put(self, event):
        self.queue.put(event)

    def register(self, type, callback):
        self.cbs[type] = callback

    def start(self):
        launch(self.loop)

    def stop(self):
        self.queue.put(None)


class Mods:

    debug = False
    dirs = {}

    @staticmethod
    def dir(name, path):
        Mods.dirs[name] = path


def command(evt):
    parse(evt, evt.txt)
    func = Commands.get(evt.cmd)
    print(func, fmt(evt))
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
        'Handler',
        'Mods',
        'command',
        'getmod',
        'modules',
        'inits',
        'scan',
        'scanner'
    )
