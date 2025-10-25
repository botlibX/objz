# This file is placed in the Public Domain.


"log text"


from objz.persist import write


class Log:
 
    pass


def log(event):
    if not event.rest:
        event.reply("log <txt>")
        return
    o = Log()
    o.txt = event.rest
    write(o)
    event.reply("ok")
    