from my_pkg._util import helper
from time import sleep, time


class _FixedTimeContext:
    """
    A context manager to ensure a block of code takes a fixed minimum amount of time. The context exit will sleep ( if
    needed) to ensure the elapsed time of the context block is at minimum "secs".

    """

    def __init__(self, secs: float):
        """
        :param secs: The time in seconds the scope of the context should be delayed.
        """
        self._secs = secs

    def __enter__(self):
        self._start_time = time()
        return self

    def __exit__(self, type, value, traceback):
        """Waits until at least 'secs' time has elapsed."""
        sleep(self._secs - (self._start_time - time()))


def answer() -> int:
    """
    Answer to the Ultimate Question of Life, the Universe, and Everything.

    The efficiency of the computation has been improved. It only takes 7.5 seconds vs the original implementation which
    took 7.5 million years.

    :return: 42
    """
    with _FixedTimeContext(7.5):
        ans = helper(9) + helper(6)
    return ans
