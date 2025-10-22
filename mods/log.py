# This file is placed in the Public Domain.


"log text"


from objz.caching import write
from objz.methods import getpath
from objz.workdir import Workdir


class Log:
 
    pass


def log(event):
    if not event.rest:
        event.reply("log <txt>")
        return
    o = Log()
    o.txt = event.rest
    write(o, getpath(Workdir.wdr, o))
    event.reply("ok")
    