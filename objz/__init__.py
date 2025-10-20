# This file is placed in the Public Domain.


"a clean namespace"


import datetime
import os


j = os.path.join


class Object:

    def __contains__(self, key):
        return key in dir(self)

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


def construct(obj, *args, **kwargs):
    if args:
        val = args[0]
        if isinstance(val, zip):
            update(obj, dict(val))
        elif isinstance(val, dict):
            update(obj, val)
        else:
            update(obj, vars(val))
    if kwargs:
        update(obj, kwargs)


def fqn(obj):
    kin = str(type(obj)).split()[-1][1:-2]
    if kin == "type":
        kin = f"{obj.__module__}.{obj.__name__}"
    return kin


def ident(obj):
    return j(fqn(obj), *str(datetime.datetime.now()).split())


def items(obj):
    if isinstance(obj, dict):
        return obj.items()
    return obj.__dict__.items()


def keys(obj):
    if isinstance(obj, dict):
        return obj.keys()
    return obj.__dict__.keys()


def update(obj, data, empty=True):
    for key, value in items(data):
        if not empty and not value:
            continue
        setattr(obj, key, value)


def values(obj):
    if isinstance(obj, dict):
        return obj.values()
    return obj.__dict__.values()


from .methods import fmt
from .serials import dump, dumps, load, loads
from .storage import elapsed, fns, fntime, read, write


def __dir__():
    return (
        'Object',
        'construct',
        'dump',
        'dumps',
        'elapsed',
        'items',
        'fmt',
        'fns',
        'fntime',
        'fqn',
        'ident',
        'keys',
        'load',
        'loads',
        'read',
        'values',
        'write',
        'update'
    )


__all__ = __dir__()
