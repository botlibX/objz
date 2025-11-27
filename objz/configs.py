# This file is placed in the Public Domain.


from .objects import Default
from .utility import getdir


class Config(Default):

    ignore = ""
    local = False
    mods = False
    name = ""
    network = False
    version = 0


__dir__ = getdir('Config')
