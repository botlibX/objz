# This file is placed in the Public Domain.


"json serializer"


import threading


from json import JSONEncoder
from json import dump  as jdump
from json import dumps as jdumps
from json import load  as jload
from json import loads as jloads


lock = threading.RLock()


class Encoder(JSONEncoder):

    def default(self, o):
        if isinstance(o, dict):
            return o.items()
        if isinstance(o, list):
            return iter(o)
        try:
            return JSONEncoder.default(self, o)
        except TypeError:
            try:
                return vars(o)
            except TypeError:
                return repr(o)



def dump(obj, *args, **kw):
    ""
    with lock:
        kw["cls"] = Encoder
        return jdump(obj, *args, **kw)


def dumps(obj, *args, **kw):
    ""
    kw["cls"] = Encoder
    return jdumps(obj, *args, **kw)


def load(*args, **kw):
    ""
    with lock:
        return jload(*args, **kw)


def loads(*args, **kw):
    ""
    return jloads(*args, **kw)


def __dir__():
    return (
        'dumps',
        'loads'
    )
