import pygame as pg
from random import randint
from ships import Player, Enemy
from settings import window, windowHeight, windowWidth, mapSize, allSprites, bullets, font, fps, particles, explosions
from meteor import Meteor
from vector2d import Vector2d
from quadtree import Quadtree

pg.init()
pg.joystick.init()

pg.display.set_caption('Space Fighters')
running = True
clock = pg.time.Clock()
stars = pg.sprite.Group()
star = pg.transform.scale(pg.image.load('png/star1.png'), (10, 10))
rect_space = pg.Rect(0, 0, mapSize, mapSize)
powering = False
last_spawn = 0
layers = []


class Camera:
    def __init__(self, f):
        self.rect = pg.Rect(0, 0, windowWidth, windowHeight)
        self.follower = f

    def move(self):
        self.rect.center = self.follower.pos.x, self.follower.pos.y
        self.rect = self.rect.clamp(rect_space)

    def offset_stars(self):
        for s in stars:
            s.rect.centerx = int(s.pos.x) - self.rect.x * s.speed
            s.rect.centery = int(s.pos.y) - self.rect.y * s.speed

    def offset(self, grp):
        for sprt in grp:
            sprt.rect.centerx = sprt.pos.x - self.rect.x
            sprt.rect.centery = sprt.pos.y - self.rect.y

    def draw(self):
        for q in layers:
            rect = self.rect.copy()
            rect.centerx = self.rect.centerx * (q.bound.w - self.rect.w) / (mapSize - self.rect.w)
            rect.centery = self.rect.centery * (q.bound.h - self.rect.h) / (mapSize - self.rect.h)

            for s in q.query(rect):
                if s.rect.colliderect(rect):
                    des = (s.rect.x / s.speed) - (self.rect.x * s.speed), (s.rect.y / s.speed) - (self.rect.y * s.speed)
                    window.blit(s.image, des)


class Star(pg.sprite.Sprite):
    def __init__(self, x, y, speed):
        super(Star, self).__init__()

        self.speed = speed
        self.image = star
        self.rect = self.image.get_rect()
        self.rect.center = x, y


def create_layer(n_stars, speed):
    w = mapSize * speed
    q = Quadtree(0, 0, w, w)

    for j in range(n_stars):
        s = Star(randint(0, w), randint(0, w), speed)
        s.add(stars)
        q.insert(s)

    return q


def add_meteors(a):
    for i in range(a):
        allSprites.add(Meteor())


def spawn_enemies():
    global last_spawn

    time = pg.time.get_ticks()
    if last_spawn + 5000 < time:
        last_spawn = time
        allSprites.add(Enemy(shp))


if __name__ == '__main__':

    shp = Player()
    allSprites.add(shp)
    camera = Camera(shp)
    add_meteors(40)
    layers.append(create_layer(300, 0.9))
    layers.append(create_layer(300, 0.5))
    layers.append(create_layer(300, 0.3))

    while running:
        window.fill((40, 40, 50))

        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False

        spawn_enemies()
        allSprites.update()
        bullets.update()

        for exp in explosions:
            exp.update()

        for bullet in bullets:
            if bullet.check_hit(allSprites):
                bullet.kill()

        camera.move()
        camera.offset(allSprites)
        camera.offset(bullets)
        camera.offset(particles)
        # camera.offset_stars()

        # stars.draw(window)
        camera.draw()
        bullets.draw(window)

        allSprites.draw(window)
        particles.draw(window)

        particles.empty()
        window.blit(font.render(str(round(1000 / clock.tick(fps))), True, (255, 255, 255)), (0, 0))
        pg.display.update()

    pg.quit()
