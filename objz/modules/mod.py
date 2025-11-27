# This file is placed in the Public Domain.


from objz.package import modules


def mod(event):
    event.reply(",".join(modules()))
