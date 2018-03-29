import math


class Vector2d:
    def __init__(self, x,  y):
        self.x = x
        self.y = y
        self.limit = None

    def add(self, other):
        self.x += other.x
        self.y += other.y

    def mult(self, h):
        self.x *= h
        self.y *= h

    def div(self, d):
        self.x /= d
        self.y /= d

    def sub(self, other):
        return Vector2d(self.x - other.x, self.y - other.y)

    def sum(self, other):
        return Vector2d(self.x + other.x, self.y + other.y)

    def norm(self):
        distance = math.sqrt(self.x * self.x + self.y * self.y)
        if distance != 0:
            self.x /= distance
            self.y /= distance

    def mag(self, m):
        self.norm()
        self.mult(m)

    def get_mag(self):
        return math.sqrt(self.x * self.x + self.y * self.y)

    def set_limit(self, v):
        self.limit = v

    def checklimit(self):
        if self.limit is not None:
            if self.get_mag() > self.limit:
                self.mag(self.limit)

    def copy(self):
        return Vector2d(self.x, self.y)

    def angle(self):
        return math.atan2(self.y, self.x)



