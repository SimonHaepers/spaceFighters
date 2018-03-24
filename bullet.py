import pygame as pg
from math import degrees
from particle import Particle
from settings import particles

laser = pg.image.load('png/laser.png')
laser_explosion = pg.image.load('png/laserGreen14.png')


class Bullet(pg.sprite.Sprite):
    def __init__(self, vector, shooter):
        super(Bullet, self).__init__()

        self.angle = shooter.angle
        self.pos = shooter.pos.copy()
        self.vel = vector.copy()
        self.image = pg.transform.rotate(laser, 270 - degrees(self.angle))
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y
        self.explosion = Particle(laser_explosion)
        self.shooter = shooter

    def update(self):
        self.pos.add(self.vel)

    def check_hit(self, group):
        for sprt in group:
            if sprt != self.shooter:
                if pg.sprite.collide_rect(self, sprt):
                    collide_pos = pg.sprite.collide_mask(self, sprt)
                    if collide_pos is not None:
                        self.explosion.draw(self.pos.x, self.pos.y, 0)  # TODO is not yet done
                        self.explosion.add(particles)
                        return True

        return False


