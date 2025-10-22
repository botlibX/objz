# This file is placed in the Public Domain.


"module management"


import importlib.util
import inspect
import logging
import os
import sys
import threading
import _thread


lock = threading.RLock()


class Mods:

    debug = False
    dirs = {}

    @staticmethod
    def dir(name, path):
        Mods.dirs[name] = path


def getmod(name):
    for nme, path in Mods.dirs.items():
        mname = nme + "." +  name
        module = sys.modules.get(mname, None)
        if module:
            return module
        pth = os.path.join(path, f"{name}.py")
        mod = importer(mname, pth)
        if mod:
            return mod


def importer(name, pth):
    if not os.path.exists(pth):
        return
    try:
        spec = importlib.util.spec_from_file_location(name, pth)
        if not spec or not spec.loader:
            return
        mod = importlib.util.module_from_spec(spec)
        if not mod:
            return
        sys.modules[name] = mod
        spec.loader.exec_module(mod)
        logging.info("load %s", pth)
        return mod
    except Exception as ex:
        logging.exception(ex)
        _thread.interrupt_main()


def modules():
    mods = []
    for name, path in Mods.dirs.items():
        if not os.path.exists(path):
            continue
        mods.extend([
            x[:-3] for x in os.listdir(path)
            if x.endswith(".py") and not x.startswith("__")
           ])
    return sorted(mods)


def __dir__():
    return (
        'Mods',
        'getmod',
        'importer',
        'modules'
    )
