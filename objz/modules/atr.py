# This file is placed in the Public Domain.


"fields"


from objz.persist import attrs
from objz.workdir import types


def atr(event):
    if not event.rest:
        res = sorted([x.split('.')[-1].lower() for x in types()])
        if res:
            event.reply(",".join(res))
        else:
            event.reply("no types")
        return
    items = attrs(event.args[0])
    if not items:
        event.reply("no fields")
    else:
        event.reply(",".join(items))
