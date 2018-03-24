import pygame as pg
from vector2d import Vector2d
from math import degrees
from settings import particles


class Particle(pg.sprite.Sprite):
    def __init__(self, img):
        super(Particle, self).__init__()

        self.pos = Vector2d(0, 0)
        self.image = img.copy()
        self.original_img = img.copy()
        self.rect = self.image.get_rect()

    def draw(self, x, y, angle):
        self.pos.x, self.pos.y = x, y
        self.image = pg.transform.rotate(self.original_img, 270 - degrees(angle))
        self.rect.size = self.image.get_size()


class Explosion:
    def __init__(self, imgs, x, y):
        self.frames = []
        for img in imgs:
            self.frames.append(Particle(img))

        self.index = 0
        self.x = x
        self.y = y

    def update(self):
        if self.index <= len(self.frames)-1:
            self.index += 0.2
            current = self.frames[int(self.index)]
            current.add(particles)
            current.draw(self.x, self.y, 0)

