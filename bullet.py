import pygame as pg
from math import atan2, degrees
from settings import allSprites
from vector2d import Vector2d

laser = pg.image.load('png/laser.png')


class Bullet(pg.sprite.Sprite):  # TODO soms verschijnt te kogel niet, het is al direct geraakt door Meteor
    def __init__(self, vector, shooter):
        super().__init__()

        self.angle = atan2(vector.y, vector.x)
        self.pos = shooter.pos.copy()
        self.vel = vector.copy()
        self.image = pg.transform.rotate(laser, 270 - degrees(self.angle))
        self.rect = self.image.get_rect()

        self.shooter = shooter

    def update(self):
        self.pos.add(self.vel)

    def check_hit(self):  # TODO group-argument maken
        for sprt in allSprites:
            if sprt != self and sprt != self.shooter:
                if pg.sprite.collide_rect(self, sprt):
                    self.kill()
