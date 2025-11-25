# This file is been placed in the Public Domain.


from objz.workdir import types


def lst(event):
    tps = types()
    if tps:
        event.reply(",".join({x.split(".")[-1].lower() for x in tps}))
    else:
        event.reply("no data yet.")
