# This file is placed in the Public Domain.


"persistence"


import datetime
import json
import os
import pathlib
import threading
import time


lock = threading.RLock()


class Workdir:

    wdr = ""


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


"path"


def cdir(path):
    pth = pathlib.Path(path)
    pth.parent.mkdir(parents=True, exist_ok=True)


def getpath(obj):
    return store(ident(obj))


def pidname(name):
    assert Workdir.wdr
    return os.path.join(Workdir.wdr, f"{name}.pid")


def skel(path):
    pth = pathlib.Path(path)
    pth.mkdir(parents=True, exist_ok=True)
    return str(pth)


def store(fnm=""):
    return os.path.join(Workdir.wdr, "store", fnm)


def types():
    path = store()
    skel(path)
    return os.listdir(path)


"find"


def find(type=None, selector=None, removed=False, matching=False):
    if selector is None:
        selector = {}
    for pth in fns(type):
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


def fns(type=None):
    if type is not None:
        type = type.lower()
    path = store()
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


"disk"


def read(obj, path):
    with lock:
        with open(path, "r", encoding="utf-8") as fpt:
            try:
                update(obj, load(fpt))
            except json.decoder.JSONDecodeError as ex:
                ex.add_note(path)
                raise ex


def write(obj, path=None):
    with lock:
        if path is None:
            path = getpath(obj)
        cdir(path)
        with open(path, "w", encoding="utf-8") as fpt:
            dump(obj, fpt, indent=4)
        Cache.update(path, obj)
        return path


"object"


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


def deleted(obj):
    return "__deleted__" in dir(obj) and obj.__deleted__


def edit(obj, setter, skip=True):
    for key, val in items(setter):
        if skip and val == "":
            continue
        try:
            setattr(obj, key, int(val))
            continue
        except ValueError:
            pass
        try:
            setattr(obj, key, float(val))
            continue
        except ValueError:
            pass
        if val in ["True", "true"]:
            setattr(obj, key, True)
        elif val in ["False", "false"]:
            setattr(obj, key, False)
        else:
            setattr(obj, key, val)


def fqn(obj):
    kin = str(type(obj)).split()[-1][1:-2]
    if kin == "type":
        kin = f"{obj.__module__}.{obj.__name__}"
    return kin


def ident(obj):
    return os.path.join(fqn(obj), *str(datetime.datetime.now()).split())


def items(obj):
    if isinstance(obj, dict):
        return obj.items()
    return obj.__dict__.items()


def keys(obj):
    if isinstance(obj, dict):
        return obj.keys()
    return obj.__dict__.keys()


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


def update(obj, data, empty=True):
    for key, value in items(data):
        if not empty and not value:
            continue
        setattr(obj, key, value)


def values(obj):
    if isinstance(obj, dict):
        return obj.values()
    return obj.__dict__.values()


"json serializer"


class Encoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, dict):
            return o.items()
        if isinstance(o, list):
            return iter(o)
        try:
            return json.JSONEncoder.default(self, o)
        except TypeError:
            try:
                return vars(o)
            except TypeError:
                return repr(o)


def dump(*args, **kw):
    ""
    kw["cls"] = Encoder
    return json.dump(*args, **kw)


def dumps(*args, **kw):
    ""
    kw["cls"] = Encoder
    return json.dumps(*args, **kw)


def load(s, *args, **kw):
    ""
    return json.load(s, *args, **kw)


def loads(s, *args, **kw):
    ""
    return json.loads(s, *args, **kw)


def __dir__():
    return (
        'Cache',
        'Object',
        'Workdir',
        'cdir',
        'construct',
        'deleted',
        'edit',
        'find',
        'fntime',
        'items',
        'keys',
        'read',
        'skel',
        'types',
        'update',
        'values',
        'write'
    )
