# This file is placed in the Public Domain.


"show modules"


from objz.modules import modules


def mod(event):
    event.reply(",".join(modules()))
