# This file is placed in the Public Domain.


from .utility import getdir


class Broker:

    objects = {}

    @staticmethod
    def add(obj):
        Broker.objects[repr(obj)] =  obj

    @staticmethod
    def all(attr=None):
        for obj in Broker.objects.values():
            if attr and attr not in dir(obj):
                continue
            yield obj

    @staticmethod
    def get(origin):
        return Broker.objects.get(origin, None)

    @staticmethod
    def like(origin):
        for orig in Broker.objects:
            if origin.split()[0] in orig.split()[0]:
                yield orig


def display(evt):
    bot = Broker.get(evt.orig)
    if bot:
        bot.display(evt)


__dir__ = getdir('Broker','display')
