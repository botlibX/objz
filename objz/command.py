# This file is placed in the Public Domain.


import importlib
import importlib.util
import inspect
import logging
import os
import os.path
import sys
import time
import _thread


from objz.clients import Client, Fleet
from objz.handler import Default, Event
from objz.persist import Workdir, pidname
from objz.threads import launch, level
from objz.utility import daemon, fmt, parse, pidfile, privileges, spl


STARTTIME = time.time()


d = os.path.dirname
j = os.path.join


"config"


class Config:

    debug = False
    init  = "irc,rss"
    level = "warn"
    name = d(d(__file__)).split(os.sep)[-1]
    verbose = False
    version = 102


"clients"


class CLI(Client):

    def __init__(self):
        Client.__init__(self)
        self.register("command", command)

    def raw(self, txt):
        print(txt.encode('utf-8', 'replace').decode("utf-8"))


class Console(CLI):

    def callback(self, event):
        if not event.txt:
            return
        super().callback(event)
        event.wait()

    def poll(self):
        evt = Event()
        evt.txt = input("> ")
        evt.type = "command"
        return evt


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
        Fleet.display(evt)
    evt.ready()


def scan(module):
    for key, cmdz in inspect.getmembers(module, inspect.isfunction):
        if key.startswith("cb"):
            continue
        if 'event' in inspect.signature(cmdz).parameters:
            Commands.add(cmdz)


"modules"


class Mods:

    dirs = {}
    

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


"scripts"


def background():
    daemon("-v" in sys.argv)
    privileges()
    boot(False)
    pidfile(pidname(Config.name))
    inits(spl(Config.init or Config.default))
    forever()


def console():
    import readline # noqa: F401
    boot()
    for _mod, thr in inits(spl(Config.init)):
        if "w" in Config.opts:
            thr.join(30.0)
    csl = Console()
    csl.start()
    forever()


def control():
    if len(sys.argv) == 1:
        return
    boot()
    csl = CLI()
    evt = Event()
    evt.orig = repr(csl)
    evt.type = "command"
    evt.txt = " ".join(sys.argv[1:])
    evt.cmd  = evt.txt.split()[0]
    command(evt)
    evt.wait()


def service():
    privileges()
    boot(False)
    pidfile(pidname(Config.name))
    inits(spl(Config.init or Config.default))
    forever()


"basic"


def banner():
    tme = time.ctime(time.time()).replace("  ", " ")
    print("%s %s since %s (%s)" % (Config.name.upper(), Config.version, tme, Config.level.upper()))


def boot(doparse=True):
    Mods.dirs["mods"] = "mods"
    Mods.dirs["objz.modules"] = j(d(__file__), "modules")
    parse(Config, " ".join(sys.argv[1:]))
    level(Config.level)
    if "v" in Config.opts:
        banner()
    if "a" in Config.opts:
        Config.init = ",".join(modules())
    Workdir.wdr = os.path.expanduser(f"~/.{Config.name}")
    scanner()
    Commands.add(cmd)
    Commands.add(ver)


def forever():
    while True:
        try:
            time.sleep(0.1)
        except (KeyboardInterrupt, EOFError):
            break


"commands"


def cmd(event):
    event.reply(",".join(Commands.cmds))


def ver(event):
    event.reply(f"{Config.name.upper()} {Config.version}")


"runtime"


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


def check(txt):
    args = sys.argv[1:]
    for arg in args:
        if not arg.startswith("-"):
            continue
        for char in txt:
            if char in arg:
                return True
    return False


def main():
    if check("c"):
        wrap(console)
    elif check("d"):
        background()
    elif check("s"):
        wrapped(service)
    else:
        wrapped(control)


"trampoline"


if __name__ == "__main__":
    main()
