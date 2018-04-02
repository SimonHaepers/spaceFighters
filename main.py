import pygame as pg
from random import randint
from math import sqrt
from ships import Player, Enemy
from settings import window, windowHeight, windowWidth, mapSize, allSprites, bullets, font, fps, particles, explosions
from meteor import Meteor
from quadtree import Quadtree

pg.init()
pg.joystick.init()

pg.display.set_caption('Space Fighters')
running = True
clock = pg.time.Clock()
stars = pg.sprite.Group()
star = pg.transform.scale(pg.image.load('png/star1.png'), (8, 8))
rect_space = pg.Rect(0, 0, mapSize, mapSize)
last_spawn = 0
layers = []


class Camera:
    def __init__(self, f):
        self.rect = pg.Rect(0, 0, windowWidth, windowHeight)
        self.r = 100
        self.follower = f

    def move(self):
        dx = self.rect.centerx - self.follower.pos.x
        dy = self.rect.centery - self.follower.pos.y
        d = sqrt(dx * dx + dy * dy)
        if d > self.r:
            dx /= d
            dy /= d
            self.rect.centerx -= dx * (d - self.r)
            self.rect.centery -= dy * (d - self.r)

        # self.rect.center = self.follower.pos.x, self.follower.pos.y

        self.rect = self.rect.clamp(rect_space)

    def offset(self, grp):
        for sprt in grp:
            sprt.rect.centerx = sprt.pos.x - self.rect.x
            sprt.rect.centery = sprt.pos.y - self.rect.y

    def draw_layers(self):
        for l in layers:
            rect = pg.Rect(0, 0, self.rect.w / l.speed, self.rect.h / l.speed)
            rect.center = self.rect.center

            for s in l.query(rect):
                if s.rect.colliderect(rect):
                    r = s.rect.copy()
                    r.centerx = mapping(s.rect.centerx, rect.left, rect.right, 0, self.rect.w)
                    r.centery = mapping(s.rect.centery, rect.top, rect.bottom, 0, self.rect.h)
                    window.blit(s.image, (r.x, r.y))


class Radar:
    def __init__(self, ship, target_group):
        self.owner = ship
        self.targets = target_group
        self.rect = pg.Rect(0, 0, 4000, 4000)
        self.image_size = 200
        self.image = pg.Surface((self.image_size, self.image_size), pg.SRCALPHA)
        self.point = pg.Surface((4, 4))
        self.point.fill((255, 0, 0))

    def update(self):
        self.image.fill(0)
        pg.draw.rect(self.image, (255, 255, 255), (1, 1, self.image_size - 2, self.image_size - 2), 1)
        self.rect.center = self.owner.pos.x, self.owner.pos.y

        for target in self.targets:
            x = mapping(target.pos.x, self.rect.left, self.rect.right, 0, self.image_size)
            y = mapping(target.pos.y, self.rect.top, self.rect.bottom, 0, self.image_size)
            self.image.blit(self.point, (x, y))


class Star(pg.sprite.Sprite):
    def __init__(self, x, y):
        super(Star, self).__init__()

        self.image = star
        self.rect = self.image.get_rect()
        self.rect.center = x, y


class Layer(Quadtree):
    def __init__(self, speed, x, y, w, h):
        Quadtree.__init__(self, x, y, w, h)

        self.speed = speed


def create_layer(is_star, n, speed):
    offset_x = windowWidth / speed - windowWidth
    offset_y = windowHeight / speed - windowHeight
    q = Layer(speed, -offset_x / 2, -offset_y / 2, mapSize + offset_x, mapSize + offset_y)

    for j in range(n):
        if is_star:
            s = Star(randint(q.bound.left, q.bound.right), randint(q.bound.top, q.bound.bottom))
        else:
            s = Meteor(speed)
        q.insert(s)

    return q


def add_meteors(a):
    for i in range(a):
        allSprites.add(Meteor(1))


def spawn_enemies():
    global last_spawn

    time = pg.time.get_ticks()
    if last_spawn + 5000 < time:
        last_spawn = time
        allSprites.add(Enemy(shp))


def respawn():
    global shp, camera, radar

    shp.kill()
    shp = Player()
    shp.add(allSprites)
    camera = Camera(shp)
    radar = Radar(shp, allSprites)
    for sprt in allSprites:
        if isinstance(sprt, Enemy):
            sprt.target = shp


def mapping(value, xmin, xmax, ymin, ymax):
    x_span = xmax - xmin
    y_span = ymax - ymin

    scaled_value = float(value - xmin) / float(x_span)

    return ymin + (scaled_value * y_span)


if __name__ == '__main__':

    shp = Player()
    allSprites.add(shp)
    camera = Camera(shp)
    radar = Radar(shp, allSprites)
    # add_meteors(200)
    layers.append(create_layer(True, 500, 0.1))
    layers.append(create_layer(False, 100, 0.2))
    layers.append(create_layer(False, 150, 0.3))
    layers.append(create_layer(False, 200, 0.4))
    layers.append(create_layer(False, 200, 0.6))

    while running:
        window.fill((40, 40, 50))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    running = False
                if event.key == pg.K_SPACE:
                    respawn()

        spawn_enemies()
        allSprites.update()
        bullets.update()

        for exp in explosions:
            exp.update()

        for bullet in bullets:
            hit = bullet.check_hit(allSprites)
            if hit is not None:
                bullet.kill()
                if isinstance(hit, Enemy):
                    shp.score += 50

        camera.move()
        camera.offset(allSprites)
        camera.offset(bullets)
        camera.offset(particles)

        camera.draw_layers()
        bullets.draw(window)
        allSprites.draw(window)
        particles.draw(window)

        particles.empty()

        score_surf = font.render(str(shp.score), True, (255, 255, 255))
        window.blit(score_surf, (windowWidth - score_surf.get_width(), 0))

        radar.update()
        window.blit(radar.image, (20, 20))

        pg.display.update()
        clock.tick(fps)

    pg.quit()
