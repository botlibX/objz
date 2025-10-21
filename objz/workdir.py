# This file is placed in the Public Domain.


"working directory"


import datetime
import os
import pathlib


d = os.path.dirname
j = os.path.join


class Workdir:

    wdr = ""


def cdir(path):
    pth = pathlib.Path(path)
    pth.parent.mkdir(parents=True, exist_ok=True)


def fqn(obj):
    kin = str(type(obj)).split()[-1][1:-2]
    if kin == "type":
        kin = f"{obj.__module__}.{obj.__name__}"
    return kin


def getname(path, nr):
    return path.split(os.sep)[-nr]


def getpath(obj):
    return store(ident(obj))


def ident(obj):
    return j(fqn(obj), *str(datetime.datetime.now()).split())


def long(name):
    split = name.split(".")[-1].lower()
    res = name
    for names in types():
        if split == names.split(".")[-1].lower():
            res = names
            break
    return res


def setwd(name, path=""):
    path = path or os.path.expanduser(f"~/.{name}")
    Workdir.wdr = Workdir.wdr or path
    skel()


def skel():
    result = ""
    if not os.path.exists(store()):
        pth = pathlib.Path(store())
        pth.mkdir(parents=True, exist_ok=True)
        result =  str(pth)
    return result


def store(pth=""):
    assert Workdir.wdr
    return j(Workdir.wdr, "store", pth)


def strip(pth, nmr=2):
    return j(pth.split(os.sep)[-nmr:])


def types():
    skel()
    return os.listdir(store())


def __dir__():
    return (
        'Workdir',
        'cdir',
        'd',
        'fqn',
        'getname',
        'getpath',
        'ident',
        'j',
        'long',
        'moddir',
        'pidfile',
        'pidname',
        'setwd',
        'skel',
        'store',
        'strip',
        'types'
    )
