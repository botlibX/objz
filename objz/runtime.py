# This file is placed in the Public Domain.
# ruff: noqa: E402


"main"


import logging
import os
import signal
import sys
import termios
import threading
import time
import _thread


signal.signal(signal.SIGINT, signal.SIG_DFL)


from objz.command import Config, Mods, command, forever, launch, parse, scanner
from objz.objects import Object, update
from objz.persist import Workdir


Mods.dir("mods", "mods")
Mods.dir("modules", os.path.join(os.path.dirname(__file__), "modules"))
Workdir.wdr = os.path.expanduser(f"~/.{Config.name}")


"logging"


LEVELS = {
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'warn': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL,
}


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


"console"


class Console:

    def loop(self):
        while True:
            try:
                event = self.poll()
                if event.txt:
                    command(event)
            except (KeyboardInterrupt, EOFError):
                _thread.interrupt_main()

    def poll(self):
        event = Event()
        event.txt = input("> ")
        return event

    def start(self):
        launch(self.loop)
        forever()


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


def banner():
    tme = time.ctime(time.time()).replace("  ", " ")
    print("%s %s since %s (%s)" % (Config.name.upper(), Config.version, tme, Config.level.upper()))


"runtime"


def boot(doparse=True):
    if doparse:
        parse(Config, " ".join(sys.argv[1:]))
    level(Config.level)


def wrapped(func):
    try:
        func()
    except (KeyboardInterrupt, EOFError):
        print("")


def wrap(func):
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
    parse(Config, txt)
    if "v" in Config.opts:
        banner()
    scanner()
    if "-c" in sys.argv:
        level(Config.level)
        csl = Console()
        csl.start()
        ewruen
    evt = Event()
    evt.txt = txt
    command(evt)


if __name__ == "__main__":
    wrap(main)
