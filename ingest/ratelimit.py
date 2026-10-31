import random
import time


class RateLimiter:
    """Garante intervalo mínimo entre requisições (60/max_per_minute) mais jitter."""

    def __init__(self, max_per_minute, jitter_s=0.0, clock=time.monotonic, sleep=time.sleep, rng=None):
        if max_per_minute <= 0:
            raise ValueError("max_per_minute deve ser > 0")
        self.min_interval = 60.0 / max_per_minute
        self.jitter_s = jitter_s
        self._clock, self._sleep = clock, sleep
        self._rng = rng or random.Random()
        self._last = None

    def wait(self):
        if self._last is not None:
            delay = self.min_interval - (self._clock() - self._last)
            if delay > 0:
                self._sleep(delay + self._rng.uniform(0, self.jitter_s))
        self._last = self._clock()
