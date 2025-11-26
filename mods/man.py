# This file is placed in the Public Domain.


"""N A M E


    %s - %s


S Y N O P S I S


    %s <cmd> [key=val] [key==val]
    %s -cvaw [init=mod1,mod2]
    %s -d
    %s -s


D E S C R I P T I O N


    %s has all you need to program a unix cli program, such as disk
    perisistence for configuration files, event handler to handle the
    client/server connection, easy programming of your own commands, etc.

    %s contains python3 code to program objects in a functional way.
    it provides an "clean namespace" Object class that only has dunder
    methods, so the namespace is not cluttered with method names. This
    makes storing and reading to/from json possible.

    %s is a python3 IRC bot, it can connect to IRC, fetch and
    display RSS feeds, take todo notes, keep a shopping list and log
    text. You can run it under systemd for 24/7 presence in a IRC channel.

    %s is Public Domain.


I N S T A L L


    installation is done with pipx

    $ pipx install %s
    $ pipx ensurepath

    <new terminal>

    $ %s srv > objz.service
    $ sudo mv %s.service /etc/systemd/system/
    $ sudo systemctl enable %s --now

    joins #%s on localhost


U S A G E 


    use %s to control the program, default it does nothing

    $ %s
    $

    see list of commands


    $ %s cmd
    cfg,cmd,dne,dpl,err,exp,imp,log,mod,mre,nme,
    pwd,rem,req,res,rss,srv,syn,tdo,thr,upt


    start console

    $ %s -c


    start console and run irc and rss 

    $ %s -c init=irc,rss

    list available modules

    $ %s mod
    err,flt,fnd,irc,llm,log,mbx,mdl,mod,req,rss,
    rst,slg,tdo,thr,tmr,udp,upt``

    start daemon

    $ %s -d
    $

    start service

    $ %s -s

    <runs until ctrl-c>


C O M M A N D S


    here is a list of available commands

    cfg - irc configuration
    cmd - commands
    dpl - sets display items
    err - show errors
    exp - export opml (stdout)
    imp - import opml
    log - log text
    mre - display cached output
    pwd - sasl nickserv name/pass
    rem - removes a rss feed
    res - restore deleted feeds
    rss - add a feed
    syn - sync rss feeds
    tdo - add todo item
    thr - show running threads
    upt - show uptime


C O N F I G U R A T I O N

    irc

    $ %s cfg server=<server>
    $ %s cfg channel=<channel>
    $ %s cfg nick=<nick>

    sasl

    $ %s pwd <nsnick> <nspass>
    $ %s cfg password=<frompwd>

    rss

    $ %s rss <url>
    $ %s dpl <url> <item1,item2>
    $ %s rem <url>
    $ %s nme <url> <name>

    opml

    $ %s exp
    $ %s imp <filename>


P R O G R A M M I N G


    %s has it's modules in the ~/.%s/mods directory so for a hello world
    command you would  edit a file in ~/.%s/mods/hello.py and add the
    following


    def hello(event):
        event.reply("hello world !!")


    typing the hello command would result into a nice hello world !!


    $ %s hello
    hello world !!


    commands run in their own thread and the program borks on exit to enable a
    short debug cycle, output gets flushed on print so exceptions appear in the
    systemd logs. modules can contain your own written python3 code.


F I L E S


    ~/.%s
    ~/.local/bin/%s
    ~/.local/pipx/venvs/%s/*


A U T H O R


    Bart Thate <bthate@dds.nl>


C O P Y R I G H T


    %s is Public Domain
"""


from objz.configs import Config


def man(event):
    if not event.rest:
        event.reply("man <description>")
        return
    descr = event.rest
    name = Config.name
    event.reply(__doc__ % (
        name.upper(),
        descr,
        *(name,) * 4,
        *(name.upper(),) * 4,
        *(name,) * 31,
        name.upper()
        ))
