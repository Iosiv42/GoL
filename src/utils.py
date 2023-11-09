""" Useful utilities for module. """

import threading
import time
from typing import TypeVar, Generic, Callable

T = TypeVar("T")


class MutexVar(Generic[T]):
    """ Wraps some variable into mutex variable.
        I.e. r/w variable with lock for eliminating race condition.
    """

    def __init__(self, inner: T):
        self.lock = threading.Lock()
        self.inner = inner

    @property
    def inner(self) -> T:
        """ Get inner variable using lock. """
        with self.lock:
            return self.__inner

    @inner.setter
    def inner(self, new_inner: T) -> None:
        with self.lock:
            self.__inner = new_inner


class PeriodicLoop(threading.Thread):
    """ Makes loop in individual thread that calls
        some func repeatedly with period T. Merely starts like normal thread.
    """

    def __init__(self, period: float, func: Callable, *func_args):
        super().__init__()

        self.sleep_event = threading.Event()
        self.func = func
        self.func_args = func_args
        self.period = MutexVar(period)
        self.__frequency = 1/period

    def run(self):
        while True:
            start = time.time()

            self.func(*self.func_args)

            delta = self.period.inner - (time.time() - start)

            self.sleep_event.wait(delta * (delta >= 0))
            self.sleep_event.clear()

    def set_frequency(self, freq: float) -> None:
        """ Set update frequency. """
        if self.__frequency != freq:
            self.period.inner = 1/freq
            self.sleep_event.set()
