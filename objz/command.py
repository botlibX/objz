# This file is placed in the Public Domain.


import inspect


from .brokers import Broker
from .methods import parse
from .objects import Object


class Commands:

    cmds = Object()
    names = Object()

    @staticmethod
    def add(*args):
        for func in args:
            name = func.__name__
            setattr(Commands.cmds, name, func)
            setattr(Commands.names, name, func.__module__.split(".")[-1])

    @staticmethod
    def get(cmd):
        return getattr(Commands.cmds, cmd, None)

    @staticmethod
    def scan(module):
        for key, cmdz in inspect.getmembers(module, inspect.isfunction):
            if key.startswith("cb"):
                continue
            if 'event' in inspect.signature(cmdz).parameters:
                Commands.add(cmdz)


def command(evt):
    parse(evt, evt.text)
    func = Commands.get(evt.cmd)
    if func:
        func(evt)
        bot = Broker.get(evt.orig)
        bot.display(evt)
    evt.ready()


def __dir__():
    return (
        'Comamnds',
        'command'
    )
