import pygame as pg
from math import degrees

laser = pg.image.load('png/laser.png')


class Bullet(pg.sprite.Sprite):  # TODO soms verschijnt te kogel niet, het is al direct geraakt door Meteor
    def __init__(self, vector, shooter):
        super(Bullet, self).__init__()

        self.angle = shooter.angle
        self.pos = shooter.pos.copy()
        self.vel = vector.copy()
        self.image = pg.transform.rotate(laser, 270 - degrees(self.angle))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y

        self.shooter = shooter

    def update(self):
        self.pos.add(self.vel)

    def check_hit(self, group):
        for sprt in group:
            if sprt != self and sprt != self.shooter:
                if pg.sprite.collide_rect(self, sprt):
                    return True

        return False


