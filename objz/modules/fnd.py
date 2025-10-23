# This file is placed in the Public Domain.


"find"


import time


from objz.methods import fmt
from objz.modules import elapsed
from objz.persist import Workdir, find, fntime, skel, types


def fnd(event):
    skel(Workdir.wdr)
    if not event.rest:
        res = sorted([x.split('.')[-1].lower() for x in types(Workdir.wdr)])
        if res:
            event.reply(",".join(res))
        else:
            event.reply("no data yet.")
        return
    otype = event.args[0]
    nmr = 0
    for fnm, obj in list(find(Workdir.wdr, otype, event.gets)):
        event.reply(f"{nmr} {fmt(obj)} {elapsed(time.time()-fntime(fnm))}")
        nmr += 1
    if not nmr:
        event.reply("no result")
