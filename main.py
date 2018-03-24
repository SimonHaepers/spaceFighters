import pygame as pg
from random import randint
from ships import Player, Enemy
from settings import windowHeight, windowWidth, mapSize, allSprites, bullets, font, fps, particles
from meteor import Meteor
from vector2d import Vector2d

pg.init()
pg.joystick.init()

window = pg.display.set_mode((windowWidth, windowHeight), pg.NOFRAME)
pg.display.set_caption('Space Fighters')
running = True
clock = pg.time.Clock()
stars = pg.sprite.Group()
star = pg.transform.scale(pg.image.load('png/star1.png'), (10, 10))
rect_space = pg.Rect(0, 0, mapSize, mapSize)
powering = False


class Camera:
    def __init__(self, f):
        self.rect = pg.Rect(0, 0, windowWidth, windowHeight)
        self.follower = f

    def move(self):
        self.rect.center = self.follower.pos.x, self.follower.pos.y
        self.rect = self.rect.clamp(rect_space)

    def move_stars(self):
        for s in stars:
            s.rect.centerx = int(s.pos.x / s.speed) - self.rect.x * s.speed
            s.rect.centery = int(s.pos.y / s.speed) - self.rect.y * s.speed

    def offset(self, grp):
        for sprt in grp:
            sprt.rect.centerx = sprt.pos.x - self.rect.x
            sprt.rect.centery = sprt.pos.y - self.rect.y


class Star(pg.sprite.Sprite):
    def __init__(self, x, y, speed):
        super(Star, self).__init__()

        self.pos = Vector2d(x, y)
        self.speed = speed
        self.image = star
        self.rect = self.image.get_rect()


def create_layer(n_stars, speed):
    for s in range(n_stars):
        Star(randint(0, speed * mapSize), randint(0, speed * mapSize), speed).add(stars)


def add_meteors(a):
    for i in range(a):
        allSprites.add(Meteor())


if __name__ == '__main__':

    shp = Player()
    enmy = Enemy(shp)
    allSprites.add(shp, enmy)
    camera = Camera(shp)
    add_meteors(40)
    create_layer(100, 0.9)
    create_layer(100, 0.5)
    create_layer(100, 0.3)

    while running:
        window.fill((40, 40, 50))

        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                running = False

        allSprites.update()
        bullets.update()

        for bullet in bullets:
            if bullet.check_hit(allSprites):
                bullet.kill()

        camera.move()
        camera.offset(allSprites)
        camera.offset(bullets)
        camera.offset(particles)
        camera.move_stars()

        stars.draw(window)
        bullets.draw(window)
        
        allSprites.draw(window)
        particles.draw(window)

        particles.empty()
        window.blit(font.render(str(round(1000 / clock.tick(fps))), True, (255, 255, 255)), (0, 0))
        pg.display.update()

    pg.quit()
