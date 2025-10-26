# This file is placed in the Public Domain.


"utilities"


import hashlib
import os
import pathlib
import sys
import time


FORMATS = [
    "%Y-%M-%D %H:%M:%S",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
    "%d-%m-%Y",
    "%d-%m",
    "%m-%d",
]


def attrs(obj, data):
    for k, v in data.items():
        setattr(obj, k, getattr(obj, k, v))


def daemon(verbose=False):
    pid = os.fork()
    if pid != 0:
        os._exit(0)
    os.setsid()
    pid2 = os.fork()
    if pid2 != 0:
        os._exit(0)
    if not verbose:
        with open('/dev/null', 'r', encoding="utf-8") as sis:
            os.dup2(sis.fileno(), sys.stdin.fileno())
        with open('/dev/null', 'a+', encoding="utf-8") as sos:
            os.dup2(sos.fileno(), sys.stdout.fileno())
        with open('/dev/null', 'a+', encoding="utf-8") as ses:
            os.dup2(ses.fileno(), sys.stderr.fileno())
    os.umask(0)
    os.chdir("/")
    os.nice(10)


def elapsed(seconds, short=True):
    txt = ""
    nsec = float(seconds)
    if nsec < 1:
        return f"{nsec:.2f}s"
    yea     = 365 * 24 * 60 * 60
    week    = 7 * 24 * 60 * 60
    nday    = 24 * 60 * 60
    hour    = 60 * 60
    minute  = 60
    yeas    = int(nsec / yea)
    nsec   -= yeas * yea
    weeks   = int(nsec / week)
    nsec   -= weeks * week
    nrdays  = int(nsec / nday)
    nsec   -= nrdays * nday
    hours   = int(nsec / hour)
    nsec   -= hours * hour
    minutes = int(nsec / minute)
    nsec   -= int(minute * minutes)
    sec     = int(nsec)
    if yeas:
        txt += f"{yeas}y"
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += f"{nrdays}d"
    if short and txt:
        return txt.strip()
    if hours:
        txt += f"{hours}h"
    if minutes:
        txt += f"{minutes}m"
    if sec:
        txt += f"{sec}s"
    txt = txt.strip()
    return txt


def extract_date(daystr):
    daystr = daystr.encode('utf-8', 'replace').decode("utf-8")
    res = time.time()
    for fmat in FORMATS:
        try:
            res = time.mktime(time.strptime(daystr, fmat))
            break
        except ValueError:
            pass
    return res


def fmt(obj, args=[], skip=[], plain=False, empty=False):
    if not args:
        args = obj.__dict__.keys()
    txt = ""
    for key in args:
        if key.startswith("__"):
            continue
        if key in skip:
            continue
        value = getattr(obj, key, None)
        if value is None:
            continue
        if not empty and not value:
            continue
        if plain:
            txt += f"{value} "
        elif isinstance(value, str):
            txt += f'{key}="{value}" '
        elif isinstance(value, (int, float, dict, bool, list)):
            txt += f"{key}={value} "
        else:
            txt += f"{key}={name(value, True)} "
    return txt.strip()


def md5sum(path):
    with open(path, "r", encoding="utf-8") as file:
        txt = file.read().encode("utf-8")
        return hashlib.md5(txt).hexdigest()


def name(obj, short=False):
    typ = type(obj)
    res = ""
    if "__builtins__" in dir(typ):
        res = obj.__name__
    elif "__self__" in dir(obj):
        res = f"{obj.__self__.__class__.__name__}.{obj.__name__}"
    elif "__class__" in dir(obj) and "__name__" in dir(obj):
        res = f"{obj.__class__.__name__}.{obj.__name__}"
    elif "__class__" in dir(obj):
        res =  f"{obj.__class__.__module__}.{obj.__class__.__name__}"
    elif "__name__" in dir(obj):
        res = f"{obj.__class__.__name__}.{obj.__name__}"
    if short:
        res = res.split(".")[-1]
    return res


def parse(obj, txt):
    attrs(obj, {
        "args": [],
        "cmd": "",
        "gets": {},
        "index": None,
        "init": "",
        "opts": "",
        "otxt": txt,
        "txt": "",
        "rest": "",
        "silent": {},
        "sets": {}
    })
    args = []
    nr = -1
    for spli in txt.split():
        if spli.startswith("-"):
            try:
                obj.index = int(spli[1:])
            except ValueError:
                obj.opts += spli[1:]
            continue
        if "-=" in spli:
            key, value = spli.split("-=", maxsplit=1)
            obj.silent[key] = value
            obj.gets[key] = value
            continue
        if "==" in spli:
            key, value = spli.split("==", maxsplit=1)
            obj.gets[key] = value
            continue
        if "=" in spli:
            key, value = spli.split("=", maxsplit=1)
            obj.sets[key] = value
            continue
        nr += 1
        if nr == 0:
            obj.cmd = spli
            continue
        args.append(spli)
    if args:
        obj.args = args
        obj.txt  = obj.cmd or ""
        obj.rest = " ".join(obj.args)
        obj.txt  = obj.cmd + " " + obj.rest
    else:
        obj.txt = obj.cmd or ""


def pidfile(filename):
    if os.path.exists(filename):
        os.unlink(filename)
    path2 = pathlib.Path(filename)
    path2.parent.mkdir(parents=True, exist_ok=True)
    with open(filename, "w", encoding="utf-8") as fds:
        fds.write(str(os.getpid()))


def privileges():
    import getpass
    import pwd
    pwnam2 = pwd.getpwnam(getpass.getuser())
    os.setgid(pwnam2.pw_gid)
    os.setuid(pwnam2.pw_uid)


def spl(txt):
    try:
        result = txt.split(",")
    except (TypeError, ValueError):
        result = [
            txt,
        ]
    return [x for x in result if x]


def __dir__():
    return (
       'daemon',
       'extract_date',
       'md5sum',
       'name',
       'privileges',
       'spl'
    )
