import pygame as pg
import math
import random
from os import walk
from vector2d import Vector2d
from settings import fps, particles, explosions, mapSize
from particle import Particle, Explosion

red_ship = pg.transform.scale(pg.image.load('png/playerShip1_red.png'), (80, 60))
fire = pg.image.load('png/fire.png')
pngs = []
for (dirpath, dirnames, files) in walk('png/enemies'):
    for file in files:
        pngs.append('png/enemies/' + file)

exps = []
for i in range(32):
    exps.append(pg.transform.scale(pg.image.load('png/explosion/expl_06_{0:04d}.png'.format(i)), (128, 128)))


class Ship(pg.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.pos = Vector2d(0, 0)
        self.vel = Vector2d(0, 0)
        self.angle = 0
        self.max_power = 30.0 / fps
        self.min_speed = 24.0 / fps
        self.max_speed = 600 / fps
        self.image = pg.Surface((50, 50))
        self.original_img = self.image.copy()
        self.rect = self.image.get_rect()
        self.last_fired = 0
        self.health = 100
        self.radius = int(math.sqrt((self.rect.centerx ** 2) + (self.rect.y ** 2)))

    def add_vel(self, vector):
        self.vel.add(vector)

        m = self.vel.get_mag()
        if m > self.max_speed:
            self.vel.mag(self.max_speed)
        elif m < self.min_speed:
            self.vel.mag(0)

    def rotate(self):
        self.image = pg.transform.rotate(self.original_img, 270 - math.degrees(self.angle))
        self.rect.size = self.image.get_size()

    def shoot(self):
        time = pg.time.get_ticks()
        if self.last_fired + 200 <= time:
            self.last_fired = time
            vel = Vector2d(math.cos(self.angle), math.sin(self.angle))
            vel.mag(1200 / fps)  # TODO change bullet arguments
            vel.add(self.vel)

            return vel

    def check_hit(self, group):
        for sprt in group:
            if sprt is not self:
                if pg.sprite.collide_rect(self, sprt):
                    if pg.sprite.collide_mask(self, sprt):
                        self.die()
                        sprt.die()

    def hit(self):
        self.health -= 20

    def die(self):
        explosions.append(Explosion(exps, self.pos.x, self.pos.y))
        self.kill()


class Player(Ship):
    def __init__(self, key=None):
        super().__init__()

        self.img_path = 'png/playerShip1_red.png'
        self.image = pg.transform.scale(pg.image.load(self.img_path), (80, 60))
        self.original_img = self.image.copy()
        self.rect = self.image.get_rect()
        self.pos = Vector2d(100, 100)
        self.max_speed = 780 / fps
        self.fire_particle = Particle(fire)
        self.score = 0
        self.alive = True
        self.key = key

    def update(self):
        self.pos.add(self.vel)
        self.rotate()
        self.rect.center = self.pos.x, self.pos.y

    def power(self):
        direction = Vector2d(math.cos(self.angle), math.sin(self.angle))
        direction.mult(self.max_power)
        self.add_vel(direction)
        x = self.pos.x + self.vel.x + math.cos(self.angle) * -random.randint(30, 40)
        y = self.pos.y + self.vel.y + math.sin(self.angle) * -random.randint(30, 40)
        self.fire_particle.draw(x, y, self.angle)
        self.fire_particle.add(particles)

    def die(self):
        explosions.append(Explosion(exps, self.pos.x, self.pos.y))
        self.kill()
        self.alive = False


class Enemy(Ship):
    def __init__(self, targets, ships, img_path=random.choice(pngs), key=None):
        super().__init__()

        self.pos = Vector2d(random.randint(0, mapSize), random.randint(0, mapSize))
        self.img_path = img_path
        self.image = pg.transform.scale(pg.image.load(self.img_path), (80, 60))
        self.original_img = self.image
        self.rect = self.image.get_rect()
        self.targets = targets
        self.ships = ships
        self.max_power = 24.0 / fps
        self.acc = Vector2d(0, 0)
        self.key = key

    def update(self):  # TODO dividing over multiple functions
        self.acc.x, self.acc.y = 0, 0
        if self.health <= 0:
            self.die()

        des = self.targets[0].pos.sub(self.pos)
        for target in self.targets:
            n_des = target.pos.sub(self.pos)
            if n_des.get_mag() < des.get_mag():
                des = n_des

        des.mag(self.max_speed)
        des = des.sub(self.vel)
        self.acc.add(des)

        sep = self.seperation(self.ships)
        sep.mag(self.max_speed)
        if sep.x != 0 or sep.y != 0:
            sep = sep.sub(self.vel)
            sep.mult(2)
            self.acc.add(sep)

        self.acc.mag(self.max_power)

        self.add_vel(self.acc)
        self.pos.add(self.vel)
        self.angle = self.vel.angle() + 3.14
        self.rotate()
        self.rect.center = self.pos.x, self.pos.y

    def seperation(self, group):  # TODO call in game class
        sum_vector = Vector2d(0, 0)
        count = 0
        for sprite in group:
            desired_seperation = (self.radius + sprite.radius) * 3
            d = math.sqrt((self.pos.x - sprite.pos.x) ** 2 + (self.pos.y - sprite.pos.y) ** 2)
            if d <= desired_seperation and sprite != self and sprite not in self.targets:
                if isinstance(sprite, Enemy):
                    push_force = 5
                else:
                    push_force = 15

                v = self.pos.sub(sprite.pos)
                v.div(push_force * d)
                sum_vector.add(v)
                count += 1

        if count != 0:
            sum_vector.div(count)
            sum_vector.norm()

        return sum_vector

