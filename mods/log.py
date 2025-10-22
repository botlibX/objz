# This file is placed in the Public Domain.


"log text"


from objz.methods import getpath

from . import Workdir, write


class Log:
 
    pass


def log(event):
    if not event.txt:
        event.reply("log <txt>")
        return
    o = Log()
    o.txt = event.txt
    write(o, getpath(Workdir.wdr, o))
    event.reply("ok")
    