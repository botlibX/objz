# This file is placed in the Public Domain.


import logging
import os
import queue
import threading
import time
import _thread


from .methods import name


class Thread(threading.Thread):

    def __init__(self, func, *args, daemon=True, **kwargs):
        super().__init__(None, self.run, None, (), daemon=daemon)
        self.event = None
        self.name = kwargs.get("name", name(func))
        self.queue = queue.Queue()
        self.result = None
        self.starttime = time.time()
        self.stopped = threading.Event()
        self.queue.put((func, args))

    def __iter__(self):
        return self

    def __next__(self):
        yield from dir(self)

    def join(self, timeout=None):
        try:
            super().join(timeout)
            return self.result
        except (KeyboardInterrupt, EOFError):
            if self.event:
                self.event.ready()
            raise ex

    def run(self):
        func, args = self.queue.get()
        if args and "ready" in dir(args[0]):
            self.event = args[0]
        try:
            self.result = func(*args)
        except Exception as ex:
            if self.event:
                self.event.ready()
            raise ex


def launch(func, *args, **kwargs):
    try:
        thread = Thread(func, *args, **kwargs)
        thread.start()
        return thread
    except (KeyboardInterrupt, EOFError):
        os._exit(0)


def threadhook(args):
    kind, value, trace, _thr = args
    exc = value.with_traceback(trace)
    if kind not in (KeyboardInterrupt, EOFError):
        logging.exception(exc)
    if _thr and _thr.event and "ready" in dir(_thr.event):
        _thr.event.ready()
    _thread.interrupt_main()


def __dir__():
    return (
        'Thread',
        'launch'
   )
