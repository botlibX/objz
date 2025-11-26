# This file is placed in the Public Domain.


import datetime
import logging
import random
import re
import time


from objz.brokers import Broker
from objz.objects import Object, items
from objz.persist import last, write
from objz.repeats import Timed
from objz.statics import MONTH
from objz.utility import elapsed, extract_date
from objz.workdir import getpath


rand = random.SystemRandom()


def init(cfg):
    Timers.path = last(Timers.timers) or getpath(Timers.timers)
    remove = []
    for tme, args in items(Timers.timers):
        orig, channel, txt = args
        for origin in Broker.like(orig):
            if not origin:
                continue
            diff = float(tme) - time.time()
            if diff > 0:
                bot = Broker.get(origin)
                timer = Timed(diff, bot.say, channel, txt)
                timer.start()
            else:
                remove.append(tme)
    for tme in remove:
        delete(tme)
    if Timers.timers:
        write(Timers.timers, Timers.path)
    logging.warning("%s timers", len(Timers.timers))


class NoDate(Exception):

    pass


class Timer(Object):

    pass


class Timers(Object):

    path = ""
    timers = Timer()



def add(tme, orig, channel,  txt):
    setattr(Timers.timers, str(tme), (orig, channel, txt))


def delete(tme):
     delattr(Timers.timers, str(tme))


def get_day(daystr):
    day = None
    month = None
    yea = None
    try:
        ymdre = re.search(r'(\d+)-(\d+)-(\d+)', daystr)
        if ymdre:
            (day, month, yea) = ymdre.groups()
    except ValueError:
        try:
            ymre = re.search(r'(\d+)-(\d+)', daystr)
            if ymre:
                (day, month) = ymre.groups()
                yea = time.strftime("%Y", time.localtime())
        except Exception as ex:
            raise NoDate(daystr) from ex
    if day:
        day = int(day)
        month = int(month)
        yea = int(yea)
        date = f"{day} {MONTH[month]} {yea}"
        return time.mktime(time.strptime(date, r"%d %b %Y"))
    raise NoDate(daystr)


def get_hour(daystr):
    try:
        hmsre = re.search(r'(\d+):(\d+):(\d+)', str(daystr))
        hours = 60 * 60 * (int(hmsre.group(1)))
        hoursmin = hours  + int(hmsre.group(2)) * 60
        hmsres = hoursmin + int(hmsre.group(3))
    except AttributeError:
        pass
    except ValueError:
        pass
    try:
        hmre = re.search(r'(\d+):(\d+)', str(daystr))
        hours = 60 * 60 * (int(hmre.group(1)))
        hmsres = hours + int(hmre.group(2)) * 60
    except AttributeError:
        return 0
    except ValueError:
        return 0
    return hmsres


def get_time(txt):
    try:
        target = get_day(txt)
    except NoDate:
        target = to_day(today())
    hour =  get_hour(txt)
    if hour:
        target += hour
    return target


def parse_time(txt):
    seconds = 0
    target = 0
    txt = str(txt)
    for word in txt.split():
        if word.startswith("+"):
            seconds = int(word[1:])
            return time.time() + seconds
        if word.startswith("-"):
            seconds = int(word[1:])
            return time.time() - seconds
    if not target:
        try:
            target = get_day(txt)
        except NoDate:
            target = to_day(today())
        hour =  get_hour(txt)
        if hour:
            target += hour
    return target


def to_day(daystr):
    previous = ""
    line = ""
    daystr = str(daystr)
    res = None
    for word in daystr.split():
        line = previous + " " + word
        previous = word
        try:
            res = extract_date(line.strip())
            break
        except ValueError:
            res = None
        line = ""
    return res


def today():
    return str(datetime.datetime.today()).split()[0]


def tmr(event):
    result = ""
    if not event.rest:
        nmr = 0
        for tme, txt in items(Timers.timers):
            lap = float(tme) - time.time()
            if lap > 0:
                event.reply(f'{nmr} {" ".join(txt)} {elapsed(lap)}')
                nmr += 1
        if not nmr:
            event.reply("no timers.")
        return result
    seconds = 0
    line = ""
    for word in event.args:
        if word.startswith("+"):
            try:
                seconds = int(word[1:])
            except (ValueError, IndexError):
                event.reply(f"{seconds} is not an integer")
                return result
        else:
            line += word + " "
    if seconds:
        target = time.time() + seconds
    else:
        try:
            target = get_day(event.rest)
        except NoDate:
            target = to_day(today())
        hour =  get_hour(event.rest)
        if hour:
            target += hour
    target += rand.random() 
    if not target or time.time() > target:
        event.reply("already passed given time.")
        return result
    diff = target - time.time()
    txt = " ".join(event.args[1:])
    add(target, event.orig, event.channel, txt)
    write(Timers.timers, Timers.path or getpath(Timers.timers))
    bot = Broker.get(event.orig)
    timer = Timed(diff, bot.say, event.orig, event.channel, txt)
    timer.start()
    event.reply("ok " +  elapsed(diff))
