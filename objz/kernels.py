# This file is placed in the Public Domain.


from .command import Commands
from .configs import Config
from .package import Mods
from .threads import launch
from .workdir import Workdir


class Kernel:

    @staticmethod
    def configure(name, version, ignore="", local=False):
        Config.name = name
        Config.version = version
        Workdir.configure(name)
        Mods.configure(f"{name}.modules", ignore, local)

    @staticmethod
    def scanner(names, init=False):
        mods = []
        for name in names:
            mod = Mods.get(name)
            if not mod:
                continue
            Commands.scan(mod)
            if init and "init" in dir(mod):
                thr = launch(mod.init, Config())
                mods.append((mod, thr))
        return mods


def __dir__():
    return (
        'Kernel',
    )
