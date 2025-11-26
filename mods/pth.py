# This file is placed in the Public Domain.


import os


from objz.configs import Config
from objz.utility import importer

def pth(event):
    mod = importer(f"{Config.name}.nucleus")
    if not mod:
        event.reply("can't find web directory.")
        return
    path = os.path.join(mod.__path__[0], "index.html")
    event.reply(f"file://{path}")
