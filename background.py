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


class LayerEncoder(json.JSONEncoder):
    def default(self, o):
        lst_objs = o.query(o.bound)
        encoded_lst_objs = []
        for obj in lst_objs:
            encoded_lst_objs.append(json.dumps(obj, cls=SpriteEncoder))

        d = {'speed': o.speed,
             'objs': encoded_lst_objs,
             'map_size': o.map_size,
             'offset_x': o.offset_x,
             'offset_y': o.offset_y
             }

        return d


def decode_sprite(dct):
    return eval(dct['cls'])(dct['size'], dct['center'][0], dct['center'][1], dct['path'])


def decode_layer(dct):
    layer = Layer(dct['speed'], dct['map_size'], dct['offset_x'], dct['offset_y'])
    for obj in dct['objs']:
        layer.insert(json.loads(obj, object_hook=decode_sprite))

    return layer


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
        self.size = 1
        self.image = self.load_image()
        self.rect = self.image.get_rect()
        self.rect.center = x, y

    def load_image(self):
        img = pg.image.load(self.path)
        return pg.transform.scale(img, (int(8 * self.size), int(8 * self.size)))


class Layer(Quadtree):
    def __init__(self, speed, map_size, offset_x, offset_y):
        Quadtree.__init__(self, -offset_x / 2, -offset_y / 2, map_size + offset_x, map_size + offset_y)

        self.speed = speed
        self.map_size = map_size
        self.offset_x = offset_x
        self.offset_y = offset_y

    def create_objs(self, n, obj):
        for j in range(n):
            s = obj(self.speed, randint(self.bound.left, self.bound.right), randint(self.bound.top, self.bound.bottom))
            self.insert(s)

