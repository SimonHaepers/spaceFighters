import pygame as pg
from math import sqrt, atan2, cos, sin
from ships import Player, Enemy
from settings import window, windowHeight, windowWidth, mapSize, fps, particles, explosions
from background import Layer, decode_layer
import socket
import json
from time import sleep
from os import walk
from random import choice
import pickle

pg.init()
pg.joystick.init()

pg.display.set_caption('Space Fighters')
running = True
clock = pg.time.Clock()
stars = pg.sprite.Group()
font = pg.font.Font('png/kenvector_future.ttf', 50)
rect_space = pg.Rect(0, 0, mapSize, mapSize)

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
        if isinstance(obj, pg.sprite.Group):
            for sprite in obj:
                window.blit(sprite.image, (sprite.rect.x - self.rect.x, sprite.rect.y - self.rect.y))
        else:
            w.blit(obj.image, (obj.rect.x - self.rect.x, obj.rect.y - self.rect.y))


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


class GameSingle(Game):
    def __init__(self, w):
        super().__init__(w)

        self.create_map()

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
            self.camera.draw_layers(self.layers, self.window)
            self.camera.draw(self.ships, self.window)
            self.camera.draw(self.bullets, self.window)
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

    def send(self, data):
        try:
            dumped_data = json.dumps(data)
            encoded_data = dumped_data.encode()
            self.socket.send(encoded_data)
        except ConnectionResetError:
            pass
        except ConnectionAbortedError:
            pass

    def receive(self):
        try:
            data = self.socket.recv(2048)
            decoded_data = data.decode()
            loaded_data = json.loads(decoded_data)
        except ConnectionResetError:
            return None
        except ConnectionAbortedError:
            return None

        return loaded_data

    def loop(self):
        while self.running:
            self.window.fill((40, 50, 50))

            self.input()

            self.player.update()
            self.update_pos()

            self.camera.move()
            self.camera.draw_layers(self.layers, self.window)
            self.camera.draw(self.player, self.window)

            pg.display.update()
            clock.tick(fps)

        self.socket.close()

    def update_pos(self):
        pass


class GameServer(GameMulti):
    def __init__(self, w):
        super().__init__(w)

        self.adress = '', 5000
        self.socket = self.connect()

        self.create_map()
        self.send_map()

    def connect(self):
        bs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bs.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        bs.settimeout(1.0)
        while True:
            try:
                print('sending...')
                bs.sendto(b'hallo', ('255.255.255.255', 5555))
                bs.recv(1024)
                print()
                print('got respond')
                break
            except socket.timeout:
                print('no respond')

        s = socket.socket()
        s.bind(self.adress)
        s.listen(1)
        sock, adress = s.accept()

        return sock

    def send_map(self):
        encoded_list = []
        for layer in self.layers:
            encoded_list.append(layer.get_dict())
        data = pickle.dumps(encoded_list)

        length = len(data)
        print('byte size: ' + str(length))
        self.socket.send(str(length + 1).encode())

        self.socket.sendall(data)

        # chunk_size = 1000
        # for i in range(0, length, chunk_size):
        #     print(i, i+chunk_size)
        #     print(data[i:i+chunk_size])
        #     self.socket.send(data[i:i+chunk_size])

    def update_pos(self):
        data = self.receive()
        if data:
            pos = int(data['pos'][0]) - self.camera.rect.x, int(data['pos'][1]) - self.camera.rect.y
            pg.draw.circle(self.window, (255, 0, 0), pos, 10)
            end_pos = int(pos[0] + cos(data['angle']) * 20), int(pos[1] + sin(data['angle']) * 20)
            pg.draw.line(self.window, (0, 0, 255), pos, end_pos, 3)

        data = {'pos': (self.player.pos.x, self.player.pos.y), 'angle': self.player.angle}
        self.send(data)


class GameClient(GameMulti):
    def __init__(self, w):
        super().__init__(w)

        self.adress = '', 5000
        self.socket = self.connect()
        print('connected to: ' + str(self.adress[0]) + ':' + str(self.adress[1]))

        self.recv_map()

    def connect(self):
        bs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bs.bind(('', 5555))

        data, adress = bs.recvfrom(1024)
        bs.sendto(b'hey', adress)

        self.adress = adress[0], self.adress[1]
        print(self.adress)
        s = socket.socket()
        s.connect(self.adress)

        return s

    def recv_map(self):
        length = int(self.socket.recv(1024).decode())
        encoded_data = b''
        while True:
            if encoded_data == length:
                break
            d = self.socket.recv(4096)
            print(d)
            encoded_data += d

            print(len(encoded_data))
        layer_list = pickle.loads(encoded_data)

        for layer_dct in layer_list:
            self.layers.append(decode_layer(layer_dct))

    def update_pos(self):
        data = {'pos': (self.player.pos.x, self.player.pos.y), 'angle': self.player.angle}
        self.send(data)

        data = self.receive()
        pos = int(data['pos'][0]) - self.camera.rect.x, int(data['pos'][1]) - self.camera.rect.y
        pg.draw.circle(self.window, (255, 0, 0), pos, 10)
        end_pos = int(pos[0] + cos(data['angle']) * 20), int(pos[1] + sin(data['angle']) * 20)
        pg.draw.line(self.window, (0, 0, 255), pos, end_pos, 3)


if __name__ == '__main__':
    game = GameServer(window)
    game.loop()

pg.quit()
