import pygame as pg
from random import randint
from quadtree import Quadtree


def decode_layer(dct):
    layer = Layer(dct['speed'], dct['map_size'], dct['offset']['x'], dct['offset']['y'])
    for obj in dct['objs']:
        layer.insert(BackgroundObj(dct['speed'], obj['pos']['x'], obj['pos']['x'], obj['path']))

    return layer


class BackgroundObj(pg.sprite.Sprite):
    def __init__(self, size, x, y, path):
        super().__init__()

        self.path = path
        self.size = size
        self.image = self.load_image()
        self.rect = self.image.get_rect()
        self.rect.center = x, y

    def load_image(self):
        img = pg.image.load(self.path)
        w = int(img.get_width() * self.size)
        h = int(img.get_height() * self.size)
        if self.path == 'png/star1.png':
            w, h = 8, 8
        return pg.transform.scale(img, (w, h))


class Layer(Quadtree):
    def __init__(self, speed, map_size, offset_x, offset_y):
        Quadtree.__init__(self, -offset_x / 2, -offset_y / 2, map_size + offset_x, map_size + offset_y)

        self.speed = speed
        self.map_size = map_size
        self.offset_x = offset_x
        self.offset_y = offset_y

    def create_objs(self, n, img_path):
        for j in range(n):
            self.insert(BackgroundObj(self.speed, randint(self.bound.left, self.bound.right),
                                      randint(self.bound.top, self.bound.bottom), img_path))

    def get_dict(self):
        lst_objs = []
        for obj in self.objs:
            lst_objs.append({'pos': {'x': obj.rect.centerx, 'y': obj.rect.centery}, 'path': obj.path})

        dct = {'speed': self.speed,
               'objs': lst_objs,
               'map_size': self.map_size,
               'offset': {'x': self.offset_x, 'y': self.offset_y}}

        return dct

