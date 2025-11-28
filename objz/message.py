# This file is placed in the Public Domain.


import threading
import time


from .objects import Default


class Message(Default):

    def __init__(self):
        super().__init__()
        self._ready = threading.Event()
        self._result = {}
        self.kind = "event"

    def ready(self):
        self._ready.set()

    def reply(self, text):
        self._result[time.time()] = text

    def wait(self, timeout=None):
        self._ready.wait(timeout)
        if self._thr:
            self._thr.join(timeout)


def __dir__():
    return (
        'Message',
    )
