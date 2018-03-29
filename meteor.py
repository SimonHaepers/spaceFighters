import pygame as pg
from os import walk
import random
from vector2d import Vector2d
from settings import mapSize

pngs = []
for (dirpath, dirnames, files) in walk('png/Meteors'):
    for file in files:
        a = pg.image.load(dirpath + '/' + file)
        pngs.append(a)


class Meteor(pg.sprite.Sprite):
    def __init__(self):
        super(Meteor, self).__init__()

        self.pos = Vector2d(random.randint(0, mapSize), random.randint(0, mapSize))
        self.vel = None

        self.image = random.choice(pngs)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y

