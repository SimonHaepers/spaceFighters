import pygame as pg
from os import walk
import random
from vector2d import Vector2d

pngs = []
for (dirpath, dirnames, files) in walk('png/Meteors'):
    for file in files:
        a = pg.image.load(dirpath + '/' + file)
        pngs.append(a)


class Meteor(pg.sprite.Sprite):
    def __init__(self):
        super(Meteor, self).__init__()

        self.image = random.choice(pngs)
        self.rect = self.image.get_rect()

        self.pos = Vector2d(random.randint(0, 4000), random.randint(0, 4000))
        self.vel = None

