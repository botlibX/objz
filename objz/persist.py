# This file is placed in the Public Domain.


import json
import os
import threading
import time


from .objects import Object, fqn, items, keys, update
from .serials import dump, load
from .utility import cdir
from .workdir import getpath, long, store


lock = threading.RLock()


class Cache:

    objs = Object()

    @staticmethod
    def add(path, obj):
        setattr(Cache.objs, path, obj)

    @staticmethod
    def get(path):
        return getattr(Cache.objs, path, None)

    @staticmethod
    def sync(path, obj):
        setattr(Cache.objs, path, obj)


def attrs(kind):
    objs = list(find(kind))
    if objs:
        return keys(objs[0][1])
    return []


def deleted(obj):
    return "__deleted__" in dir(obj) and obj.__deleted__


def find(kind=None, selector=None, removed=False, matching=False):
    if selector is None:
        selector = {}
    fullname = long(kind)
    for pth in fns(fullname):
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


def fns(kind=None):
    if kind is not None:
        kind = kind.lower()
    path = store()
    for rootdir, dirs, _files in os.walk(path, topdown=True):
        for dname in dirs:
            if dname.count("-") != 2:
                continue
            ddd = os.path.join(rootdir, dname)
            if kind and kind not in ddd.lower():
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


def last(obj, selector=None):
    if selector is None:
        selector = {}
    result = sorted(
                    find(fqn(obj), selector),
                    key=lambda x: fntime(x[0])
                   )
    res = ""
    if result:
        inp = result[-1]
        update(obj, inp[-1])
        res = inp[0]
    return res


def read(obj, path):
    with lock:
        with open(path, "r", encoding="utf-8") as fpt:
            try:
                update(obj, load(fpt))
            except json.decoder.JSONDecodeError as ex:
                ex.add_note(path)
                raise ex


def search(obj, selector, matching=False):
    res = False
    for key, value in items(selector):
        val = getattr(obj, key, None)
        if not val:
            continue
        if matching and value == val:
            res = True
        elif str(value).lower() in str(val).lower():
            res = True
        else:
            res = False
            break
    return res


def write(obj, path=None):
    with lock:
        if path is None:
            path = getpath(obj)
        cdir(path)
        with open(path, "w", encoding="utf-8") as fpt:
            dump(obj, fpt, indent=4)
        Cache.sync(path, obj)
        return path


def __dir__():
    return (
        'Cache',
        'attrs',
        'deleted',
        'find',
        'fns',
        'fntime',
        'last',
        'read',
        'search',
        'write'
    )
