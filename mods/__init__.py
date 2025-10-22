# This file is placed in the Public Domain.


import importlib.util
import inspect
import json
import json.decoder
import logging
import os
import pathlib
import readline
import sys
import threading
import time
import _thread


from objz.methods import deleted, name, search
from objz.objects import Object, update
from objz.serials import dump, load


NAME = "objz"


LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


lock = threading.RLock()


class Workdir:

    wdr = ""


class Formatter(logging.Formatter):

    def format(self, record):
        record.module = record.module.upper()
        return logging.Formatter.format(self, record)


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


def launch(func, *args, **kwargs):
    thread = threading.Thread(None, func, name(func), *args, **kwargs)
    thread.start()
    return thread


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


class Cache:

    objs = {}

    @staticmethod
    def add(path, obj):
        Cache.objs[path] = obj

    @staticmethod
    def get(path):
        return Cache.objs.get(path, None)

    @staticmethod
    def update(path, obj):
        if path in Cache.objs:
            update(Cache.objs[path], obj)
        else:
            Cache.add(path, obj)


def cdir(path):
    pth = pathlib.Path(path)
    pth.parent.mkdir(parents=True, exist_ok=True)


def find(path, type=None, selector=None, removed=False, matching=False):
    if selector is None:
        selector = {}
    for pth in fns(path, type):
        obj = Cache.get(pth)
        if not obj:
            obj = Object()
            read(obj, pth)
            Cache.add(pth, obj)
        if not removed and deleted(obj):
            continue
        if selector and not search(obj, selector, matching):
            continue
        yield pth, obj


def fns(path, type=None):
    if type is not None:
        type = type.lower()
    for rootdir, dirs, _files in os.walk(path, topdown=True):
        for dname in dirs:
            if dname.count("-") != 2:
                continue
            ddd = os.path.join(rootdir, dname)
            if type and type not in ddd.lower():
                continue
            for fll in os.listdir(ddd):
                yield os.path.join(ddd, fll)


def fntime(daystr):
    datestr = " ".join(daystr.split(os.sep)[-2:])
    datestr = datestr.replace("_", " ")
    if "." in datestr:
        datestr, rest = datestr.rsplit(".", 1)
    else:
        rest = ""
    timed = time.mktime(time.strptime(datestr, "%Y-%m-%d %H:%M:%S"))
    if rest:
        timed += float("." + rest)
    return float(timed)


def long(path, name):
    split = name.split(".")[-1].lower()
    res = name
    for names in types(path):
        if split == names.split(".")[-1].lower():
            res = names
            break
    return res


def read(obj, path):
    with lock:
        with open(path, "r", encoding="utf-8") as fpt:
            try:
                update(obj, load(fpt))
            except json.decoder.JSONDecodeError as ex:
                ex.add_note(path)
                raise ex


def skel(path):
    pth = pathlib.Path(path)
    pth.mkdir(parents=True, exist_ok=True)
    return str(pth)


def types(path):
    skel(path)
    return os.listdir(path)


def write(obj, path):
    with lock:
        cdir(path)
        with open(path, "w", encoding="utf-8") as fpt:
            dump(obj, fpt, indent=4)
        Cache.update(path, obj)
        return path


# This file is placed in the Public Domain.

"objects"


import os
import signal
import sys
import termios
import time


signal.signal(signal.SIGINT, signal.SIG_DFL)


Mods.dir("mods", "mods")


class Config:

    debug = False
    init  = ""
    level = "warn"
    name = NAME
    verbose = False
    version = 102


Workdir.wdr = os.path.expanduser(f"~/.{Config.name}")


class Console:

    def loop(self):
        while True:
            try:
                event = Event()
                event.txt = input("> ")
                command(event)
            except (KeyboardInterrupt, EOFError):
                _thread.interrupt_main()

    def start(self):
        launch(self.loop)


def banner():
    tme = time.ctime(time.time()).replace("  ", " ")
    print("%s %s since %s (%s)" % (Config.name.upper(), Config.version, tme, Config.level.upper()))


def wrapped(func):
    try:
        func()
    except (KeyboardInterrupt, EOFError):
        print("")


def wrap(func):
    import termios
    old = None
    try:
        old = termios.tcgetattr(sys.stdin.fileno())
    except termios.error:
        pass
    try:
        wrapped(func)
    finally:
        if old:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)


def main():
    txt = " ".join(sys.argv[1:])
    if not txt:
        os._exit(0)
    scanner()
    if "-c" in sys.argv:
        banner()
        level(Config.level)
        csl = Console()
        csl.start()
    else:
        evt = Event()
        evt.txt = txt
        command(evt)
