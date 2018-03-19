import pygame as pg
from ships import Player, Enemy
from settings import windowHeight, windowWidth, mapSize, allSprites, bullets, font
from meteor import Meteor
from vector2d import Vector2d

pg.init()
pg.joystick.init()

window = pg.display.set_mode((windowWidth, windowHeight))
pg.display.set_caption('Space Fighters')
running = True
clock = pg.time.Clock()
backgrounds = pg.sprite.Group()
background = pg.image.load('png/background.png')
rect_space = pg.Rect(0, 0, mapSize, mapSize)
powering = False


class Camera:
    def __init__(self, f):
        self.rect = pg.Rect(0, 0, windowWidth, windowHeight)
        self.follower = f

    def move(self):
        self.rect.center = self.follower.pos.x, self.follower.pos.y
        self.rect = self.rect.clamp(rect_space)

    def offset(self, grp):
        for sprt in grp:
            sprt.rect.centerx = sprt.pos.x - self.rect.x
            sprt.rect.centery = sprt.pos.y - self.rect.y


class Background(pg.sprite.Sprite):  # TODO beter en sneller maken
    def __init__(self, x, y):
        pg.sprite.Sprite.__init__(self)

        self.image = background
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.pos = Vector2d(self.rect.centerx, self.rect.centery)


def add_meteors(a):  # TODO setup-functie maken
    for i in range(a):
        allSprites.add(Meteor())


def make_bg():
    bgw = background.get_width()
    bgh = background.get_height()

    for x in range(int(mapSize / bgw)):
        for y in range(int(mapSize / bgh)):
            backgrounds.add(Background(x * bgw, y * bgh))


if __name__ == '__main__':

    shp = Player()
    enmy = Enemy(shp)
    allSprites.add(shp, enmy)
    camera = Camera(shp)
    add_meteors(40)
    make_bg()

    while running:
        window.fill((0, 0, 0))

        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False

        allSprites.update()

        camera.move()
        camera.offset(allSprites)  # TODO collision detection with absolute position
        camera.offset(backgrounds)

        for bullet in bullets:
            bullet.check_hit(allSprites)

        backgrounds.draw(window)
        allSprites.draw(window)

        window.blit(font.render(str(clock.tick(60)), True, (255, 255, 255)), (0, 0))
        pg.display.update()

    pg.quit()
