# This file is placed in the Public Domain.


from objz.package import Mods


def mod(event):
    event.reply(",".join(Mods.modules()))
