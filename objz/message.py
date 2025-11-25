# This file is placed in the Public Domain.


import threading
import time
import _thread


from .objects import Default, Object


class Message(Default):

    def __init__(self):
        super().__init__()
        self._ready = threading.Event()
        self.result = {}
        self.kind = "event"

    def ready(self):
        self._ready.set()

    def reply(self, text):
        self.result[time.time()] = text

    def wait(self, timeout=None):
        self._ready.wait(timeout)
        if self._thr:
            self._thr.join(timeout)


def __dir__():
    return (
        'Message',
   )
