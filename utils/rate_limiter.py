import time

class RateLimiter:
    def __init__(self, max_requests_per_second):
        self.min_interval = 1.0 / max_requests_per_second
        self.last_call = time.time()

    def wait(self):
        now = time.time()
        elapsed = now - self.last_call
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_call = time.time()