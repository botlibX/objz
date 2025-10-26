# This file is placed in the Public Domain.


"handle events"


import queue
import threading
import time
import _thread


from objz.threads import launch


class Default:

    def __contains__(self, key):
        return key in dir(self)

    def __getattr__(self, key):
        return self.__dict__.get(key, "")

    def __iter__(self):
        return iter(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __str__(self):
        return str(self.__dict__)


class Event(Default):

    def __init__(self):
        Default.__init__(self)
        self._ready = threading.Event()
        self._thr = None
        self.channel = ""
        self.ctime = time.time()
        self.orig = ""
        self.result = {}
        self.txt = ""
        self.type = "event"

    def ready(self):
        self._ready.set()

    def reply(self, txt):
        self.result[time.time()] = txt

    def wait(self, timeout=None):
        try:
            self._ready.wait()
            if self._thr:
                self._thr.join(timeout)
        except (KeyboardInterrupt, EOFError):
            _thread.interrupt_main()


class Handler:

    def __init__(self):
        self.cbs = {}
        self.queue = queue.Queue()

    def callback(self, event):
        func = self.cbs.get(event.type, None)
        if func:
            name = event.txt and event.txt.split()[0]
            event._thr = launch(func, event, name=name)
        else:
            event.ready()

    def loop(self):
        while True:
            try:
                event = self.poll()
                if event is None:
                    break
                event.orig = repr(self)
                self.callback(event)
            except (KeyboardInterrupt, EOFError):
                _thread.interrupt_main()

    def poll(self):
        return self.queue.get()

    def put(self, event):
        self.queue.put(event)

    def register(self, type, callback):
        self.cbs[type] = callback

    def start(self):
        launch(self.loop)

    def stop(self):
        self.queue.put(None)


def __dir__():
    return (
        'Event',
        'Handler'
   )
