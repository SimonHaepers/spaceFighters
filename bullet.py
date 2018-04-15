import pygame as pg
from math import degrees, atan2
from particle import Particle
from settings import particles, mapSize

laser_explosion = pg.image.load('png/laserGreen14.png')


class Bullet(pg.sprite.Sprite):
    def __init__(self, pos, vector, shooter, key=None):
        super().__init__()

        self.pos = pos.copy()
        self.vel = vector.copy()
        self.angle = atan2(self.vel.y, self.vel.x)
        self.path = 'png/laser.png'
        self.image = pg.transform.rotate(pg.image.load(self.path), 270 - degrees(self.angle))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y
        self.explosion = Particle(laser_explosion)
        self.shooter = shooter
        self.key = key

    def update(self):
        self.pos.add(self.vel)
        self.rect.center = self.pos.x, self.pos.y

        if self.pos.x > mapSize or self.pos.x < 0 or self.pos.y > mapSize or self.pos.y < 0:
            self.kill()

    def check_hit(self, group):
        for sprt in group:
            if sprt != self.shooter:
                if pg.sprite.collide_rect(self, sprt):
                    collide_pos = pg.sprite.collide_mask(self, sprt)
                    if collide_pos is not None:
                        self.explosion.draw(self.pos.x + collide_pos[0], self.pos.y + collide_pos[1], 0)
                        self.explosion.add(particles)
                        if hasattr(sprt, 'hit'):
                            sprt.hit()

                        return sprt

        return None

    def hit(self):
        self.explosion.draw(self.pos.x, self.pos.y, 0)
        self.explosion.add(particles)
        self.kill()
