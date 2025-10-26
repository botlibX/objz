# This file is placed in the Public Domain.


"manual"


TXT = """
N A M E


    TOB - bot in reverse !


S Y N O P S I S


    objr <cmd> [key=val] [key==val]
    objr -cvaw [init=mod1,mod2]
    objr -d
    objr -s


D E S C R I P T I O N


    TOB has all you need to program a unix cli program, such as disk
    perisistence for configuration files, event handler to handle the
    client/server connection, easy programming of your own commands, etc.

    TOB contains python3 code to program objects in a functional way.
    it provides an "clean namespace" Object class that only has dunder
    methods, so the namespace is not cluttered with method names. This
    makes storing and reading to/from json possible.

    TOB is a python3 IRC bot, it can connect to IRC, fetch and
    display RSS feeds, take todo notes, keep a shopping list and log
    text. You can run it under systemd for 24/7 presence in a IRC channel.

    TOB is Public Domain.


I N S T A L L


    installation is done with pipx

    $ pipx install objr
    $ pipx ensurepath

    <new terminal>

    $ objr srv > tob.service
    $ sudo mv objr.service /etc/systemd/system/
    $ sudo systemctl enable objr --now

    joins #objr on localhost


U S A G E 


    use objr to control the program, default it does nothing

    $ objr
    $

    see list of commands


    $ objr cmd
    cfg,cmd,dne,dpl,err,exp,imp,log,mod,mre,nme,
    pwd,rem,req,res,rss,srv,syn,tdo,thr,upt


    start console

    $ objr -c


    start console and run irc and rss 

    $ objr -c init=irc,rss

    list available modules

    $ objr mod
    err,flt,fnd,irc,llm,log,mbx,mdl,mod,req,rss,
    rst,slg,tdo,thr,tmr,udp,upt``

    start daemon

    $ objr -d
    $

    start service

    $ objr -s

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

    $ objr cfg server=<server>
    $ objr cfg channel=<channel>
    $ objr cfg nick=<nick>

    sasl

    $ objr pwd <nsnick> <nspass>
    $ objr cfg password=<frompwd>

    rss

    $ objr rss <url>
    $ objr dpl <url> <item1,item2>
    $ objr rem <url>
    $ objr nme <url> <name>

    opml

    $ objr exp
    $ objr imp <filename>


P R O G R A M M I N G


    objr has it's modules in the ~/.tob/mods directory so for a hello world
    command you would  edit a file in ~/.objr/mods/hello.py and add the
    following


    def hello(event):
        event.reply("hello world !!")


    typing the hello command would result into a nice hello world !!


    $ objr hello
    hello world !!


    commands run in their own thread and the program borks on exit to enable a
    short debug cycle, output gets flushed on print so exceptions appear in the
    systemd logs. modules can contain your own written python3 code.


F I L E S


    ~/.objr
    ~/.local/bin/objr
    ~/.local/pipx/venvs/objr/*


A U T H O R


    Bart Thate <bthate@dds.nl>


C O P Y R I G H T


    TOB is Public Domain
"""


def man(event):
    event.reply(TXT)
