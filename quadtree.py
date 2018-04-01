import pygame as pg


class Quadtree:
    def __init__(self, x, y, w, h):
        self.bound = pg.Rect(x, y, w, h)
        self.divided = False
        self.limit = 20
        self.objs = pg.sprite.Group()
        self.nodes = []

    def insert(self, obj):
        if self.intersect(obj):
            if not self.divided and len(self.objs) < self.limit:
                self.objs.add(obj)
            else:
                if not self.divided:
                    self.divide()
                for node in self.nodes:
                    node.insert(obj)

    def divide(self):
        w = self.bound.w / 2
        h = self.bound.h / 2

        self.nodes = [Quadtree(self.bound.x, self.bound.y, w, h),
                      Quadtree(self.bound.centerx, self.bound.y, w, h),
                      Quadtree(self.bound.x, self.bound.centery, w, h),
                      Quadtree(self.bound.centerx, self.bound.centery, w, h)
                      ]

        self.divided = True

    def intersect(self, obj):
        # r = obj.rect.move(obj.pos.x - obj.rect.w / 2, obj.pos.y - obj.rect.h / 2)
        return self.bound.colliderect(obj.rect)

    def query(self, rect):
        group = pg.sprite.Group()

        if rect.colliderect(self.bound):
            group.add(self.objs)
            if self.divided:
                for node in self.nodes:
                    group.add(node.query(rect))

        return group

