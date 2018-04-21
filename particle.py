import pygame as pg
from math import degrees


class Particle(pg.sprite.Sprite):
    def __init__(self, img, x, y, angle):
        super(Particle, self).__init__()

        self.image = pg.transform.rotate(img, 270 - degrees(angle))
        self.rect = self.image.get_rect()
        self.rect.center = x, y


class Explosion:
    def __init__(self, imgs, x, y):
        self.frames = []
        for img in imgs:
            self.frames.append(Particle(img, x, y, 0))

        self.index = 0
        self.x = x
        self.y = y

    def update(self):
        if self.index <= len(self.frames)-1:
            self.index += 0.4
            current = self.frames[int(self.index)]
            return current

        return None


