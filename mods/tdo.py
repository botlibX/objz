# This file is placed in the Public Domain.


"todo items"


from objz.persist import Workdir, find, getpath, write


class Todo:

    pass


def dne(event):
    if not event.args:
        event.reply("dne <txt>")
        return
    selector = {'txt': event.args[0]}
    nmr = 0
    for fnm, obj in find("todo", selector):
        nmr += 1
        obj.__deleted__ = True
        write(obj, fnm)
        event.reply("ok")
        break
    if not nmr:
        event.reply("nothing todo")


def tdo(event):
    if not event.rest:
        event.reply("tdo <txt>")
        return
    obj = Todo()
    obj.txt = event.rest
    write(obj)
    event.reply("ok")
