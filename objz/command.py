# This file is placed in the Public Domain.


import inspect


from .brokers import Broker
from .methods import parse


class Commands:

    cmds = {}
    names = {}

    @staticmethod
    def add(*args):
        for func in args:
            name = func.__name__
            Commands.cmds[name] = func
            Commands.names[name] = func.__module__.split(".")[-1]

    @staticmethod
    def get(cmd):
        return Commands.cmds.get(cmd, None)

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
        Broker.display(evt)
    evt.ready()


def __dir__():
    return (
        'Comamnds',
        'command'
    )
