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
        for l in layers:
            rect = pg.Rect(0, 0, self.rect.w / l.speed, self.rect.h / l.speed)
            rect.center = self.rect.center

            for s in l.query(rect):
                r = s.rect.copy()
                r.centerx = mapping(s.pos.x - rect.x, 0, rect.w, 0, self.rect.w)
                r.centery = mapping(s.pos.y - rect.y, 0, rect.h, 0, self.rect.h)
                # pg.draw.rect(window, (255, 0, 0), r)
                window.blit(s.image, (r.x, r.y))


class Star(pg.sprite.Sprite):
    def __init__(self, x, y):
        super(Star, self).__init__()

        self.pos = Vector2d(x, y)
        self.image = star
        self.rect = self.image.get_rect()
        self.rect.center = self.pos.x, self.pos.y


class Layer(Quadtree):
    def __init__(self, speed, x, y, w, h):
        super(Layer, self).__init__(x, y, w, h)

        self.speed = speed


def create_layer(n_stars, speed):
    q = Layer(speed, 0, 0, mapSize, mapSize)

    for j in range(n_stars):
        s = Star(randint(0, mapSize), randint(0, mapSize))
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


def mapping(value, xmin, xmax, ymin, ymax):
    x_span = xmax - xmin
    y_span = ymax - ymin

    scaled_value = float(value - xmin) / float(x_span)

    return ymin + (scaled_value * y_span)


if __name__ == '__main__':

    shp = Player()
    allSprites.add(shp)
    camera = Camera(shp)
    add_meteors(40)
    layers.append(create_layer(200, 0.9))
    layers.append(create_layer(150, 0.5))
    layers.append(create_layer(100, 0.3))

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
