# This file is placed in the Public Domain.


"handle events"


import queue
import threading
import time
import _thread


from objz.methods import name


class Event:

    def __init__(self):
        self._olock = threading.RLock()
        self._ready = threading.Event()
        self._thr = None
        self.args = []
        self.channel = ""
        self.ctime = time.time()
        self.orig = ""
        self.rest = ""
        self.result = {}
        self.txt = ""
        self.type = "event"

    def display(self):
        with self._olock:
            for tme in sorted(self.result):
                print(self.result[tme])

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


class Engine:

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


class Client(Engine):

    def __init__(self):
        Engine.__init__(self)
        self.olock = threading.RLock()
        self.oqueue = queue.Queue()
        self.silent = True
        Fleet.add(self)

    def announce(self, txt):
        if not self.silent:
            self.raw(txt)

    def display(self, event):
        with self.olock:
            for tme in sorted(event.result):
                self.dosay(
                           event.channel,
                           event.result[tme]
                          )

    def dosay(self, channel, txt):
        self.say(channel, txt)

    def raw(self, txt):
        raise NotImplementedError("raw")

    def say(self, channel, txt):
        self.raw(txt)


class Output(Client):

    def output(self):
        while True:
            event = self.oqueue.get()
            if event is None:
                self.oqueue.task_done()
                break
            self.display(event)
            self.oqueue.task_done()

    def start(self):
        launch(self.output)
        super().start()

    def stop(self):
        self.oqueue.put(None)
        super().stop()

    def wait(self):
        try:
            self.oqueue.join()
        except Exception:
            _thread.interrupt_main()


def forever():
    while True:
        try:
            time.sleep(0.1)
        except (KeyboardInterrupt, EOFError):
            break


def launch(func, *args, **kwargs):
    thread = threading.Thread(None, func, name(func), tuple(args), dict(kwargs), daemon=True)
    thread.start()
    return thread


def __dir__():
    return (
        'Client',
        'Engine',
        'Event',
        'Output'
        'forever',
        'launch'
   )
