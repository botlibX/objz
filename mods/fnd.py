# This file is placed in the Public Domain.


"find"


import time


from objz.objects import fmt
from objz.persist import find, fntime, skel, store, types
from objz.repeats import elapsed


def fnd(event):
    skel(store())
    if not event.rest:
        res = sorted([x.split('.')[-1].lower() for x in types()])
        if res:
            event.reply(",".join(res))
        else:
            event.reply("no data yet.")
        return
    otype = event.args[0]
    nmr = 0
    for fnm, obj in list(find(otype, event.gets)):
        event.reply(f"{nmr} {fmt(obj)} {elapsed(time.time()-fntime(fnm))}")
        nmr += 1
    if not nmr:
        event.reply("no result")
