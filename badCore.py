import digitalio
import time
# !! core.py has not been fully restored. Some classes and functions are missing. !!
class button:
    OFF, PRESSED, RELEASED, HELD = 3, 2, 1, 0
    def __init__(self, pin):
        btn = digitalio.DigitalInOut(pin)
        btn.direction = digitalio.Direction.INPUT
        btn.pull = digitalio.Pull.UP
        self.btn = btn
        self.last = True
    def get(self):
        status = 0
        if self.last:
            status += 2
        if self.btn.value:
            status += 1
        self.last = self.btn.value
        return status
class countdown:
    def __init__(self, t):
        self.reset(t)
    def reset(self, t):
        self.start = time.monotonic_ns()
        self.finish = self.start + t * 1000000000
    def precisereset(self, t): #accounts for time spent between expirechk and reset, reccomended for tick counters
        self.start = time.monotonic_ns()
        self.finish += t * 1000000000
    def percent(self): #used to display time as a float between 0 and 1
        return (self.finish - time.monotonic_ns()) / (self.finish - self.start)
    def secsleft(self): #used to say how many seconds timer has left
        return (self.finish - time.monotonic_ns()) / 1000000000
    def expirechk(self):
        return time.monotonic_ns() > self.finish