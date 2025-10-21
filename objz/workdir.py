# This file is placed in the Public Domain.


"object for a string"


import os
import pathlib
import time


from .objects import Object


def cdir(path):
    pth = pathlib.Path(path)
    pth.parent.mkdir(parents=True, exist_ok=True)


def fns(path):
    for rootdir, dirs, _files in os.walk(path, topdown=False):
        for dname in dirs:
            if dname.count("-") != 2:
                continue
            ddd = os.path.join(rootdir, dname)
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


def last(path, selector=None):
    if selector is None:
        selector = {}
    result = sorted(
                    find(path, selector),
                    key=lambda x: fntime(x[0])
                   )
    res = ""
    if result:
        inp = result[-1]
        update(obj, inp[-1])
        res = inp[0]
    return res


def long(path, name):
    split = name.split(".")[-1].lower()
    res = name
    for names in types(path):
        if split == names.split(".")[-1].lower():
            res = names
            break
    return res


def skel(path):
    pth = pathlib.Path(path)
    pth.mkdir(parents=True, exist_ok=True)
    return str(pth)


def types(path):
    skel(path)
    return os.listdir(path)


def __dir__():
    return (
        'cdir',
        'find',
        'fns',
        'last',
        'long',
        'skel',
        'types'
    )
