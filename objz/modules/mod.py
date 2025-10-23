# This file is placed in the Public Domain.


"show modules"


from objz.runtime import modules


def mod(event):
    event.reply(",".join(modules()))
