# This file is placed in the Public Domain.


"uptime"


import time


from objz.command import STARTTIME
from objz.utility import elapsed


def upt(event):
    event.reply(elapsed(time.time()-STARTTIME))
