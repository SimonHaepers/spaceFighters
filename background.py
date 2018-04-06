import pygame as pg
from os import walk
from random import randint, choice
from quadtree import Quadtree
import json

star = pg.transform.scale(pg.image.load('png/star1.png'), (8, 8))
meteor_pngs = []
for (dirpath, dirnames, files) in walk('png/Meteors'):
    for file in files:
        meteor_pngs.append(dirpath + '/' + file)


class SpriteEncoder(json.JSONEncoder):
    def default(self, o):
        d = {'center': o.rect.center,
             'path': o.path,
             'size': o.size,
             'cls': o.__class__.__name__
             }
        return d


def decode_sprite(dct):
    return eval(dct['cls'])(dct['size'], dct['center'][0], dct['center'][1], dct['path'])


class Meteor(pg.sprite.Sprite):
    def __init__(self, size, x, y, path=None):
        super(Meteor, self).__init__()

        if path:
            self.path = path
        else:
            self.path = choice(meteor_pngs)

        self.size = size
        self.image = self.load_image()
        self.rect = self.image.get_rect()
        self.rect.center = x, y

    def load_image(self):
        img = pg.image.load(self.path)
        w = int(img.get_width() * self.size)
        h = int(img.get_height() * self.size)
        return pg.transform.scale(img, (w, h))


class Star(pg.sprite.Sprite):
    def __init__(self, size, x, y):
        super(Star, self).__init__()

        self.path = 'png/star1.png'
        self.size = size
        self.image = self.load_image()
        self.rect = self.image.get_rect()
        self.rect.center = x, y

    def load_image(self):
        img = pg.image.load(self.path)
        return pg.transform(img, (8 * self.size, 8 * self.size))


class Layer(Quadtree):
    def __init__(self, speed, n, obj, map_size, window_width, window_heigt):
        offset_x = window_width / speed - window_width
        offset_y = window_heigt / speed - window_heigt

        Quadtree.__init__(self, -offset_x / 2, -offset_y / 2, map_size + offset_x, map_size + offset_y)

        self.speed = speed
        for j in range(n):
            s = obj(speed, randint(self.bound.left, self.bound.right), randint(self.bound.top, self.bound.bottom))
            self.insert(s)

