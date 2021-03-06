import math

class Transitioner(object):
    def __init__(self, curr, min_step_size = 1):
        self.current = curr
        self.start = curr
        self.end = curr
        self.step_size = 0
        self.min_step_size = min_step_size
        self.hasMinMax = False

    def setMinMax(self, min, max):
        self.hasMinMax = True
        self.max = max
        self.min = min

    def transitionFromStart(self, delta, steps):
        self.current = self.start
        self.end = self.start + delta
        self.step_size = math.copysign(max(1, abs(delta) / max(1, steps)), delta)

    def transition(self, end, steps):
        self.end = end
        delta = self.end - self.current
        self.step_size = math.copysign(max(1, abs(delta) / max(1, steps)), delta)
        if self.hasMinMax:
            if self.step_size > 0:
                self.end = min(self.end, self.max)
            else:
                self.end = max(self.end, self.min)

    def revert(self, steps):
        self.end = self.start
        delta = self.end - self.current
        self.step_size = math.copysign(max(1, abs(delta) / max(1, steps)), delta)

    def update(self):
        if self.step_size > 0 and self.current < self.end:
            self.current += self.step_size
            self.current = min(self.current, self.end)
        elif self.step_size < 0 and self.current > self.end:
            self.current += self.step_size
            self.current = max(self.current, self.end)
        return self.current

    def isDone(self):
        return self.current == self.end
