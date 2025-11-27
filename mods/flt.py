# This file is placed in the Public Domain.


from objz.brokers import Broker
from objz.methods import fmt
from objz.threads import name


def flt(event):
    clts = Broker.all("announce")
    if event.args:
        index = int(event.args[0])
        if index < len(clts):
            event.reply(fmt(list(clts)[index]), empty=True)
        else:
            event.reply(f"only {len(clts)} clients in fleet.")
        return
    event.reply(' | '.join([name(o) for o in clts]))
