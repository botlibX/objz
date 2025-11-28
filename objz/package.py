# This file is placed in the Public Domain.


import os
import sys


from .configs import Config
from .utility import importer, spl
from .workdir import moddir


class Mods:

    dirs = {}
    ignore = ""
    package = __spec__.parent
    path = os.path.dirname(__spec__.loader.path)

    @staticmethod
    def add(name, path):
        Mods.dirs[name] = path

    @staticmethod
    def configure():
        name = Mods.package + ".modules" 
        Mods.add(name, os.path.join(Mods.path, "modules"))
        Mods.add("modules", moddir())
        if "n" in Config.opts:
            name = Mods.package + ".network" 
            Mods.add(name, os.path.join(Mods.path, "network"))
        if "m" in Config.opts:
            Mods.add("mods", "mods")

    @staticmethod
    def get(name):
        mname = ""
        pth = ""
        if name in spl(Mods.ignore):
            return
        for packname, path in Mods.dirs.items():
            modpath = os.path.join(path, name + ".py")
            if os.path.exists(modpath):
                pth = modpath
                mname = f"{packname}.{name}"
                break
        return sys.modules.get(mname, None) or importer(mname, pth)


def modules():
    mods = []
    for name, path in Mods.dirs.items():
        if name in spl(Mods.ignore):
            continue
        if not os.path.exists(path):
            continue
        mods.extend([
            x[:-3] for x in os.listdir(path)
            if x.endswith(".py") and not x.startswith("__") and x not in spl(Mods.ignore)
        ])
    return sorted(mods)


def __dir__():
    return (
        'Mods',
        'modules'
    )
