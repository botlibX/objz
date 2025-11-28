# This file is placed in the Public Domain.


from .objects import Default


class Config(Default):

    debug = False
    ignore = ""
    local = False
    mods = False
    name = ""
    network = False
    version = 0


def __dir__():
    return (
        'Config',
    )
