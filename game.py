import pygame as pg
from math import sqrt, atan2, degrees
from ships import Player, Enemy
from settings import window, windowHeight, windowWidth, mapSize, fps, particles, explosions
from background import Layer, decode_layer
import socket
from os import walk
from random import choice, randint
import pickle
from bullet import Bullet
from vector2d import Vector2d
from quadtree import Quadtree

pg.init()
pg.joystick.init()

pg.display.set_caption('Space Fighters')
running = True
clock = pg.time.Clock()
font = pg.font.Font('png/kenvector_future.ttf', 50)
rect_space = pg.Rect(0, 0, mapSize, mapSize)
keys_dict = {}
used_keys = []
collision_tree = Quadtree(0, 0, mapSize, mapSize)

meteor_pngs = []
for (dirpath, dirnames, files) in walk('png/Meteors'):
    for file in files:
        meteor_pngs.append(dirpath + '/' + file)


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

    def draw_layers(self, layers, w):
        for l in layers:
            rect = pg.Rect(0, 0, self.rect.w / l.speed, self.rect.h / l.speed)
            rect.center = self.rect.center

            for s in l.query(rect):
                if s.rect.colliderect(rect):
                    r = s.rect.copy()
                    r.centerx = mapping(s.rect.centerx, rect.left, rect.right, 0, self.rect.w)
                    r.centery = mapping(s.rect.centery, rect.top, rect.bottom, 0, self.rect.h)
                    w.blit(s.image, (r.x, r.y))

    def draw(self, obj, w):
        if isinstance(obj, list) or isinstance(obj, pg.sprite.Group):
            for sprite in obj:
                window.blit(sprite.image, (sprite.rect.x - self.rect.x, sprite.rect.y - self.rect.y))
        else:
            w.blit(obj.image, (obj.rect.x - self.rect.x, obj.rect.y - self.rect.y))


class Radar:
    def __init__(self, ship, target_groups):
        self.owner = ship
        self.groups = target_groups
        self.rect = pg.Rect(0, 0, 4000, 4000)
        self.image_size = 200
        self.image = pg.Surface((self.image_size, self.image_size), pg.SRCALPHA)

    def update(self):
        self.image.fill(0)
        pg.draw.rect(self.image, (255, 255, 255), (1, 1, self.image_size - 2, self.image_size - 2), 1)
        self.rect.center = self.owner.pos.x, self.owner.pos.y

        for targets in self.groups:
            for target in targets:
                x = mapping(target.rect.centerx, self.rect.left, self.rect.right, 0, self.image_size)
                y = mapping(target.rect.centery, self.rect.top, self.rect.bottom, 0, self.image_size)
                pg.draw.rect(self.image, (255, 0, 0), (x, y, 4, 4))


def mapping(value, xmin, xmax, ymin, ymax):
    x_span = xmax - xmin
    y_span = ymax - ymin

    scaled_value = float(value - xmin) / float(x_span)

    return ymin + (scaled_value * y_span)


def check_collision(group):
    checks = 0
    mask_checks = 0
    collision_tree.clear()
    for sprite in group:
        collision_tree.insert(sprite)

    collision_list = []
    for sprite in group:
        for other in collision_tree.query(sprite.rect):
            if sprite != other:
                checks += 1
                if pg.sprite.collide_rect(sprite, other):
                    mask_checks += 1
                    if pg.sprite.collide_mask(sprite, other):
                        collision_list.append((sprite, other))

    return collision_list


class Game:
    def __init__(self, w):
        self.window = w
        self.running = True
        self.player = Player()
        self.camera = Camera(self.player)
        self.ships = pg.sprite.Group()
        self.ships.add(self.player)
        self.bullets = pg.sprite.Group()
        self.radar = Radar(self.player, [self.ships])

        self.layers = []

        self.last_spawn = 0

        if pg.joystick.get_count() != 0:
            self.joystick = pg.joystick.Joystick(0)
            self.joystick.init()
            self.mode_joystick = True
        else:
            self.mode_joystick = False

    def create_map(self):
        self.layers.append(Layer(0.1, mapSize, windowWidth / 0.1 - windowWidth, windowHeight / 0.1 - windowHeight))
        self.layers.append(Layer(0.2, mapSize, windowWidth / 0.2 - windowWidth, windowHeight / 0.1 - windowHeight))
        self.layers.append(Layer(0.3, mapSize, windowWidth / 0.3 - windowWidth, windowHeight / 0.1 - windowHeight))
        self.layers.append(Layer(0.4, mapSize, windowWidth / 0.4 - windowWidth, windowHeight / 0.1 - windowHeight))
        self.layers.append(Layer(0.6, mapSize, windowWidth / 0.6 - windowWidth, windowHeight / 0.1 - windowHeight))
        self.layers[0].create_objs(100, 'png/star1.png')
        self.layers[1].create_objs(50, choice(meteor_pngs))
        self.layers[2].create_objs(75, choice(meteor_pngs))
        self.layers[3].create_objs(100, choice(meteor_pngs))
        self.layers[4].create_objs(100, choice(meteor_pngs))

    def input(self):
        for event in pg.event.get():
            if event.type == pg.JOYBUTTONDOWN and event.button == 8 or \
                    event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                self.running = False

        if self.player.alive:
            if self.mode_joystick:
                if self.joystick.get_button(4):
                    shot = self.player.shoot()
                    if shot:
                        self.add_bullet(self.player, shot)
                if self.joystick.get_button(5):
                    self.player.power()

                x = self.joystick.get_axis(0)
                y = self.joystick.get_axis(1)

            else:
                buttons = pg.mouse.get_pressed()
                if buttons[0] == 1:
                    self.player.power()
                if buttons[2] == 1:
                    shot = self.player.shoot()
                    if shot:
                        self.add_bullet(self.player, shot)

                mouse_pos = pg.mouse.get_pos()
                x = mouse_pos[0] - (self.player.rect.centerx - self.camera.rect.x)
                y = mouse_pos[1] - (self.player.rect.centery - self.camera.rect.y)

            self.player.angle = atan2(y, x)

    def spawn_enemy(self):
        time = pg.time.get_ticks()
        if self.last_spawn + 5000 < time:
            self.last_spawn = time
            self.ships.add(Enemy([self.player], self.ships))

    def add_bullet(self, shooter, vel):
        self.bullets.add(Bullet(shooter.pos, vel, self.player))


class GameSingle(Game):
    def __init__(self, w):
        super().__init__(w)

        self.create_map()

    def loop(self):  # TODO divide into smaller functions
        while self.running:
            print()
            self.window.fill((40, 50, 50))

            self.input()

            self.spawn_enemy()

            for ship in self.ships:
                ship.update()

            self.bullets.update()
            for exp in explosions:
                exp.update()

            for enemy in self.ships:  # TODO kill sprites here
                enemy.check_hit(self.ships)

            for bullet in self.bullets:
                hit = bullet.check_hit(self.ships)
                if hit:
                    bullet.kill()
                    if isinstance(hit, Enemy):
                        self.player.score += 50

            self.camera.move()
            self.camera.draw_layers(self.layers, self.window)
            self.camera.draw(self.bullets, self.window)
            self.camera.draw(self.ships, self.window)
            self.camera.draw(particles, self.window)

            particles.empty()

            score_surf = font.render(str(self.player.score), True, (255, 255, 255))
            self.window.blit(score_surf, (windowWidth - score_surf.get_width(), 0))

            self.radar.update()
            self.window.blit(self.radar.image, (20, 20))

            pg.display.update()
            clock.tick(fps)


class GameMulti(Game):
    def __init__(self, w):
        super().__init__(w)

        self.socket = socket.socket()
        self.send_list = []

        self.player = Player(get_key())
        self.send_list.append(AddEvent(self.player.img_path, self.player.rect.size, self.player.key, 'player'))

        self.camera = Camera(self.player)
        self.ships = []
        self.ghost_bullets = []
        self.ghost_ships = []
        self.ghost_players = []
        self.ships.append(self.player)
        self.bullets = []
        self.radar = Radar(self.player, [self.ships, self.ghost_ships])

    def send(self, data):
        encoded_data = pickle.dumps(data)
        self.socket.send(encoded_data)

    def receive(self):
        data = None
        try:
            data = pickle.loads(self.socket.recv(2048))
        except EOFError:
            self.running = False

        if data:
            for event in data:
                if isinstance(event, AddEvent):
                    if event.obj == 'ship':
                        event.do(self.ghost_ships)
                    elif event.obj == 'player':
                        event.do(self.ghost_players)

                elif isinstance(event, ShootEvent):
                    event.do(self.ghost_bullets)

                else:
                    event.do()

    def spawn_enemy(self):  # TODO make better
        time = pg.time.get_ticks()
        if self.last_spawn + 5000 < time:
            self.last_spawn = time
            ship = Enemy([self.player] + self.ghost_players, self.ships, key=get_key())  # TODO fix this
            self.ships.append(ship)
            self.send_list.append(AddEvent(ship.img_path, ship.rect.size, ship.key, 'ship'))

    def add_bullet(self, shooter, vel):
        bullet = Bullet(shooter.pos, vel, shooter, get_key())
        self.bullets.append(bullet)
        self.send_list.append(ShootEvent(bullet.pos, bullet.vel, bullet.key))


class GameServer(GameMulti):
    def __init__(self, w, sock):
        super().__init__(w)

        self.socket = sock

        self.create_map()
        self.send_map()

    def loop(self):
        while self.running:
            self.window.fill((40, 50, 50))

            self.input()

            self.spawn_enemy()

            for ship in self.ships:
                ship.update()
                self.send_list.append(MoveEvent(ship.key, ship.pos, ship.angle))
            for bullet in self.bullets:
                bullet.update()

            all_sprites = self.ships + self.bullets + self.ghost_ships + self.ghost_bullets + self.ghost_players
            handled = []
            for collision in check_collision(all_sprites):
                for sprite in collision:
                    if sprite not in handled:
                        # sprite.hit()
                        handled.append(sprite)

            self.receive()
            self.send(self.send_list)

            for ghost in self.ghost_ships + self.ghost_bullets + self.ghost_players:
                ghost.update()

            self.camera.move()
            self.camera.draw_layers(self.layers, self.window)
            self.camera.draw(self.player, self.window)
            self.camera.draw(all_sprites, self.window)

            self.radar.update()
            self.window.blit(self.radar.image, (20, 20))

            pg.display.update()
            self.send_list = []
            clock.tick(fps)

        self.socket.close()

    def send_map(self):
        encoded_list = []
        for layer in self.layers:
            encoded_list.append(layer.get_dict())
        data = pickle.dumps(encoded_list)

        length = len(data)
        print('byte size: ' + str(length))
        self.socket.sendall(str(length).encode())

        self.socket.sendall(data)


class GameClient(GameMulti):
    def __init__(self, w, sock):
        super().__init__(w)

        self.socket = sock

        self.recv_map()

    def loop(self):
        while self.running:
            self.window.fill((40, 50, 50))

            self.input()

            for ship in self.ships:
                ship.update()
                self.send_list.append(MoveEvent(ship.key, ship.pos, ship.angle))

            for bullet in self.bullets:
                bullet.update()

            self.send(self.send_list)
            self.receive()

            for ghost in self.ghost_ships + self.ghost_bullets + self.ghost_players:
                ghost.update()

            self.camera.move()
            self.camera.draw_layers(self.layers, self.window)
            self.camera.draw(self.player, self.window)
            self.camera.draw(self.ghost_ships + self.ghost_bullets + self.ghost_players, self.window)
            self.camera.draw(self.bullets + self.ships, self.window)

            self.radar.update()
            self.window.blit(self.radar.image, (20, 20))

            pg.display.update()
            self.send_list = []
            clock.tick(fps)

        self.socket.close()

    def recv_map(self):
        length = int(self.socket.recv(1024).decode())
        encoded_data = b''
        while True:
            if len(encoded_data) == length:
                break
            d = self.socket.recv(8192)
            encoded_data += d

        layer_list = pickle.loads(encoded_data)

        for layer_dct in layer_list:
            self.layers.append(decode_layer(layer_dct))


class AddEvent:
    def __init__(self, img_path, img_size, key, obj):
        self.img_path = img_path
        self.img_size = img_size
        self.key = key
        self.obj = obj

    def do(self, group):
        shp = Ghost(self.img_path, self.img_size)
        keys_dict[self.key] = shp
        used_keys.append(self.key)
        group.append(shp)


class MoveEvent:
    def __init__(self, key, pos, angle):
        self.key = key
        self.pos = pos.copy()
        self.angle = angle

    def do(self):
        obj = keys_dict[self.key]
        obj.pos = self.pos
        obj.angle = self.angle


class ShootEvent:
    def __init__(self, pos, vel, key):
        self.pos = pos.copy()
        self.vel = vel.copy()
        self.key = key

    def do(self, group):
        bullet = Bullet(self.pos, self.vel, None, self.key)
        keys_dict[self.key] = bullet
        group.append(bullet)


def get_key():
    key = str(randint(0, 255))
    while key in used_keys:
        key = str(randint(0, 255))

    used_keys.append(key)

    return key


class Ghost(pg.sprite.Sprite):
    def __init__(self, img_path, img_size):
        super().__init__()

        self.pos = Vector2d(0, 0)
        self.image = pg.image.load(img_path)
        if img_size:
            self.image = pg.transform.scale(self.image, img_size)
        self.original_img = self.image.copy()
        self.rect = self.image.get_rect()
        self.angle = 0

    def update(self):
        self.image = pg.transform.rotate(self.original_img, 270 - degrees(self.angle))
        self.rect.size = self.image.get_size()
        self.rect.center = self.pos.x, self.pos.y

    def hit(self):
        pass


if __name__ == '__main__':
    GameSingle(window).loop()
    pg.quit()
