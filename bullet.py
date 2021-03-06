import pygame as pg
from math import degrees
from particle import Particle
from settings import mapSize

laser_explosion = pg.image.load('png/laserGreen14.png')


class Bullet(pg.sprite.Sprite):
    def __init__(self, pos, vector, angle, shooter, key=None):
        super().__init__()

        self.pos = pos.copy()
        self.vel = vector.copy()
        self.angle = angle
        self.path = 'png/laser.png'
        self.image = pg.transform.rotate(pg.image.load(self.path), 270 - degrees(self.angle))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y
        self.shooter = shooter
        self.key = key
        self.alive = True

    def update(self):
        self.pos.add(self.vel)
        self.rect.center = self.pos.x, self.pos.y

        if self.pos.x > mapSize or self.pos.x < 0 or self.pos.y > mapSize or self.pos.y < 0:
            self.kill()

    def check_hit(self, sprite):
        if sprite != self.shooter:
            sprite.hit()
            return self.die()

    def die(self):
        self.alive = False
        return Particle(laser_explosion, self.pos.x, self.pos.y, 0)
