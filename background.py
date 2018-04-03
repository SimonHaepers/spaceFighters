import pygame as pg
from os import walk
from random import randint, choice
from quadtree import Quadtree

star = pg.transform.scale(pg.image.load('png/star1.png'), (8, 8))
pngs = []
for (dirpath, dirnames, files) in walk('png/Meteors'):
    for file in files:
        a = pg.image.load(dirpath + '/' + file)
        pngs.append(a)


class Meteor(pg.sprite.Sprite):
    def __init__(self, size, x, y):
        super(Meteor, self).__init__()

        img = choice(pngs)
        w = int(img.get_width() * size)
        h = int(img.get_height() * size)
        self.image = pg.transform.scale(img, (w, h))
        self.rect = self.image.get_rect()
        self.rect.center = x, y


class Star(pg.sprite.Sprite):
    def __init__(self, size, x, y):
        super(Star, self).__init__()

        self.image = star
        self.rect = self.image.get_rect()
        self.rect.center = x, y
        self.size = size


class Layer(Quadtree):
    def __init__(self, speed, n, obj, map_size, window_width, window_heigt):
        offset_x = window_width / speed - window_width
        offset_y = window_heigt / speed - window_heigt

        Quadtree.__init__(self, -offset_x / 2, -offset_y / 2, map_size + offset_x, map_size + offset_y)

        self.speed = speed
        for j in range(n):
            s = obj(speed, randint(self.bound.left, self.bound.right), randint(self.bound.top, self.bound.bottom))
            self.insert(s)

