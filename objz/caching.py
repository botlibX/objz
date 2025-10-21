# This file is placed in the Public Domain.


"object for a string"


import json.decoder
import os
import pathlib
import threading
import time


from .methods import deleted, getpath, ident, search
from .objects import Object, update
from .serials import dump, load


j    = os.path.join
lock = threading.RLock()


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


"utilities"


def cdir(path):
    pth = pathlib.Path(path)
    pth.parent.mkdir(parents=True, exist_ok=True)


def find(path, selector=None, removed=False, matching=False):
    if selector is None:
        selector = {}
    for pth in fns(path):
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


def fns(path):
    for rootdir, dirs, _files in os.walk(path, topdown=False):
        for dname in dirs:
            if dname.count("-") != 2:
                continue
            ddd = j(rootdir, dname)
            for fll in os.listdir(ddd):
                yield j(ddd, fll)


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


"methods"


def read(obj, path):
    with lock:
        with open(path, "r", encoding="utf-8") as fpt:
            try:
                update(obj, load(fpt))
            except json.decoder.JSONDecodeError as ex:
                ex.add_note(path)
                raise ex



def write(obj, path):
    with lock:
        cdir(path)
        with open(path, "w", encoding="utf-8") as fpt:
            dump(obj, fpt, indent=4)
        Cache.update(path, obj)
        return path


def __dir__():
    return (
        'Cache',
        'find',
        'last',
        'read',
        'write'
    )
