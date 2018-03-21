import pygame as pg
import math
import random
from os import walk
from vector2d import Vector2d
from settings import allSprites, bullets, windowWidth, windowHeight
from bullet import Bullet

red_ship = pg.image.load('png/playerShip1_red.png')
pngs = []
for (dirpath, dirnames, files) in walk('png/enemies'):
    for file in files:
        a = pg.image.load(dirpath + '/' + file)
        pngs.append(a)


class Ship(pg.sprite.Sprite):
    def __init__(self):
        super(Ship, self).__init__()

        self.pos = Vector2d(0, 0)
        self.vel = Vector2d(0, 0)
        self.angle = 0
        self.max_power = 0.5
        self.max_speed = 10
        self.image = pg.Surface((50, 50))
        self.original_img = self.image
        self.rect = self.image.get_rect()

    def add_vel(self, vector, power):
        vector.mag(power)
        self.vel.add(vector)

        m = self.vel.get_mag()
        if m > self.max_speed:
            self.vel.mag(self.max_speed)
        elif m < 0.4:
            self.vel.mag(0)

    def rotate(self):
        self.image = pg.transform.rotate(self.original_img, 270 - math.degrees(self.angle))
        self.rect.size = self.image.get_size()


class Player(Ship):
    def __init__(self):
        super(Player, self).__init__()

        self.image = red_ship
        self.original_img = self.image
        self.rect = self.image.get_rect()
        self.pos = Vector2d(100, 100)
        self.max_speed = 13

        if pg.joystick.get_count() != 0:
            self.joystick = pg.joystick.Joystick(0)
            self.joystick.init()
            self.mode_joystick = True
        else:
            self.mode_joystick = False

    def update(self):
        if self.mode_joystick:
            mouse_angle = math.atan2(self.joystick.get_axis(1), self.joystick.get_axis(0))
            if self.joystick.get_button(5):
                self.power()
            if self.joystick.get_button(4):
                self.shoot()
        else:
            mouse_pos = pg.mouse.get_pos()
            mouse_angle = math.atan2(mouse_pos[1] - windowHeight/2, mouse_pos[0] - windowWidth/2)
            buttons = pg.mouse.get_pressed()
            if buttons[0]:
                self.power()
            if buttons[2]:
                self.shoot()

        self.angle = mouse_angle

        self.pos.add(self.vel)

        self.rotate()

    def power(self):
        direction = Vector2d(math.cos(self.angle), math.sin(self.angle))
        self.add_vel(direction, self.max_power)

    def shoot(self):
        vel = Vector2d(math.cos(self.angle), math.sin(self.angle))
        vel.mag(20)
        vel.add(self.vel)
        Bullet(vel, self).add(allSprites, bullets)


class Enemy(Ship):
    def __init__(self, target):
        super(Enemy, self).__init__()

        self.pos = Vector2d(1000, 1000)
        self.image = random.choice(pngs)
        self.original_img = self.image
        self.rect = self.image.get_rect()
        self.target = target
        self.max_power = 0.4

    def update(self):
        des = self.target.pos.sub(self.pos)
        des.mag(10)
        steering = des.sub(self.vel)
        self.add_vel(steering, self.max_power)

        self.pos.add(self.vel)
        self.angle = self.vel.angle() + 3.14
        self.rotate()