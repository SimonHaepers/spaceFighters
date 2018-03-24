import pygame as pg
from vector2d import Vector2d
from math import degrees


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
