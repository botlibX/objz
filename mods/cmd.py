# This file is placed in the Public Domain.


"list of commands"


from objz.command import Commands


def cmd(event):
    event.reply(",".join(Commands.cmds))
