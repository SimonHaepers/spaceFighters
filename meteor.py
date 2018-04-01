import pygame as pg
from os import walk
from random import randint, choice
from vector2d import Vector2d
from settings import mapSize
from math import sqrt

pngs = []
for (dirpath, dirnames, files) in walk('png/Meteors'):
    for file in files:
        a = pg.image.load(dirpath + '/' + file)
        pngs.append(a)


class Meteor(pg.sprite.Sprite):
    def __init__(self, size):
        super(Meteor, self).__init__()

        self.pos = Vector2d(randint(0, mapSize), randint(0, mapSize))
        self.vel = None

        img = choice(pngs)
        w = int(img.get_width() * size)
        h = int(img.get_height() * size)
        self.image = pg.transform.scale(img, (w, h))
        self.rect = self.image.get_rect()
        self.radius = int(sqrt((self.rect.centerx ** 2) + (self.rect.y ** 2)))
        self.rect.center = self.pos.x, self.pos.y

