import pygame as pg
from math import sqrt, atan2
from ships import Player, Enemy
from settings import window, windowHeight, windowWidth, mapSize, fps, particles, explosions
from background import Layer, Star, Meteor

pg.init()
pg.joystick.init()

pg.display.set_caption('Space Fighters')
running = True
clock = pg.time.Clock()
stars = pg.sprite.Group()
font = pg.font.Font('png/kenvector_future.ttf', 50)
rect_space = pg.Rect(0, 0, mapSize, mapSize)


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

        self.rect = self.rect.clamp(rect_space)

    def offset(self, grp):
        for sprt in grp:
            sprt.rect.centerx = sprt.pos.x - self.rect.x
            sprt.rect.centery = sprt.pos.y - self.rect.y

    def draw_layers(self, layers):
        for l in layers:
            rect = pg.Rect(0, 0, self.rect.w / l.speed, self.rect.h / l.speed)
            rect.center = self.rect.center

            for s in l.query(rect):
                if s.rect.colliderect(rect):
                    r = s.rect.copy()
                    r.centerx = mapping(s.rect.centerx, rect.left, rect.right, 0, self.rect.w)
                    r.centery = mapping(s.rect.centery, rect.top, rect.bottom, 0, self.rect.h)
                    window.blit(s.image, (r.x, r.y))

    def draw(self, obj):
        if isinstance(obj, pg.sprite.Group):
            for sprite in obj:
                window.blit(sprite.image, (sprite.rect.x - self.rect.x, sprite.rect.y - self.rect.y))
        else:
            window.blit(obj.image, (obj.rect.x - self.rect.x, obj.rect.y - self.rect.y))


class Radar:
    def __init__(self, ship, target_group):
        self.owner = ship
        self.targets = target_group
        self.rect = pg.Rect(0, 0, 4000, 4000)
        self.image_size = 200
        self.image = pg.Surface((self.image_size, self.image_size), pg.SRCALPHA)

    def update(self):
        self.image.fill(0)
        pg.draw.rect(self.image, (255, 255, 255), (1, 1, self.image_size - 2, self.image_size - 2), 1)
        self.rect.center = self.owner.pos.x, self.owner.pos.y

        for target in self.targets:
            x = mapping(target.pos.x, self.rect.left, self.rect.right, 0, self.image_size)
            y = mapping(target.pos.y, self.rect.top, self.rect.bottom, 0, self.image_size)
            pg.draw.rect(self.image, (255, 0, 0), (x, y, 4, 4))


def mapping(value, xmin, xmax, ymin, ymax):
    x_span = xmax - xmin
    y_span = ymax - ymin

    scaled_value = float(value - xmin) / float(x_span)

    return ymin + (scaled_value * y_span)


class Game:
    def __init__(self, w):
        self.window = w
        self.running = True
        self.player = Player()
        self.camera = Camera(self.player)
        self.ships = pg.sprite.Group()
        self.ships.add(self.player)
        self.bullets = pg.sprite.Group()
        self.radar = Radar(self.player, self.ships)

        self.layers = []
        self.layers.append(Layer(0.1, 500, Star, mapSize, windowHeight, windowWidth))
        self.layers.append(Layer(0.2, 100, Meteor, mapSize, windowHeight, windowWidth))
        self.layers.append(Layer(0.3, 150, Meteor, mapSize, windowHeight, windowWidth))
        self.layers.append(Layer(0.4, 200, Meteor, mapSize, windowHeight, windowWidth))
        self.layers.append(Layer(0.6, 200, Meteor, mapSize, windowHeight, windowWidth))

        self.last_spawn = 0

        if pg.joystick.get_count() != 0:
            self.joystick = pg.joystick.Joystick(0)
            self.joystick.init()
            self.mode_joystick = True
        else:
            self.mode_joystick = False

    def loop(self):  # TODO divide into smaller functions
        while self.running:
            self.window.fill((40, 50, 50))

            self.input()

            self.spawn_enemy()

            self.ships.update()
            self.bullets.update()
            for exp in explosions:
                exp.update()

            for enemy in self.ships:  # TODO kill sprites here
                enemy.check_hit(self.ships)

            for bullet in self.bullets:
                hit = bullet.check_hit(self.ships)
                if hit is not None:
                    bullet.kill()
                    if isinstance(hit, Enemy):
                        self.player.score += 50

            self.camera.move()
            self.camera.draw_layers(self.layers)
            self.camera.draw(self.ships)
            self.camera.draw(self.bullets)
            self.camera.draw(particles)

            particles.empty()

            score_surf = font.render(str(self.player.score), True, (255, 255, 255))
            self.window.blit(score_surf, (windowWidth - score_surf.get_width(), 0))

            self.radar.update()
            self.window.blit(self.radar.image, (20, 20))

            pg.display.update()
            clock.tick(fps)

    def input(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or event.type == pg.JOYBUTTONDOWN and event.button == 8:
                self.running = False

        if self.player.alive:
            if self.mode_joystick:
                if self.joystick.get_button(4):
                    bullet = self.player.shoot()
                    if bullet:
                        bullet.add(self.bullets)
                if self.joystick.get_button(5):
                    self.player.power()

                x = self.joystick.get_axis(0)
                y = self.joystick.get_axis(1)

            else:
                buttons = pg.mouse.get_pressed()
                if buttons[0] == 1:
                    self.player.power()
                if buttons[2] == 1:
                    bullet = self.player.shoot()
                    if bullet:
                        bullet.add(self.bullets)

                mouse_pos = pg.mouse.get_pos()
                x = mouse_pos[0] - (self.player.rect.centerx - self.camera.rect.x)
                y = mouse_pos[1] - (self.player.rect.centery - self.camera.rect.y)

            self.player.angle = atan2(y, x)

    def spawn_enemy(self):
        time = pg.time.get_ticks()
        if self.last_spawn + 5000 < time:
            self.last_spawn = time
            self.ships.add(Enemy(self.player, self.ships))


if __name__ == '__main__':
    game = Game(window)
    game.loop()

pg.quit()
