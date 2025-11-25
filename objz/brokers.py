# This file is placed in the Public Domain.


from .objects import Object, values


class Broker:

    objects = Object()

    @staticmethod
    def add(obj):
        setattr(Broker.objects, repr(obj), obj)

    @staticmethod
    def get(origin):
        return getattr(Broker.objects, origin, None)

    @staticmethod
    def all(attr=None):
        for obj in values(Broker.objects):
            if attr and attr not in dir(obj):
                continue
            yield obj

    @staticmethod
    def like(origin):
        for orig in Broker.objects:
            if origin.split()[0] in orig.split()[0]:
                yield orig


def __dir__():
    return (
        'Broker',
    )
