import pygame as pg
from math import degrees
from particle import Particle
from settings import particles, mapSize, bullets

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
                        return True

        return False


