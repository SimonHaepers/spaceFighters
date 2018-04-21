import pygame as pg
from settings import windowWidth, windowHeight
from GUI import Window, Button, Text
from game import GameSingle, GameServer, GameClient
import socket

pg.init()

window = pg.display.set_mode((windowWidth, windowHeight))
running = True
window_log = []

font = pg.font.Font('png/kenvector_future.ttf', 50)
button_img = pg.image.load('png/buttonRed.png')


def stop():
    global running
    running = False


def play_single():
    score = GameSingle(window).loop()
    game_over_window.widgets.append(Text('score: ' + str(score), windowWidth/2, 200))
    window_log.insert(0, game_over_window)


def play_multi():
    window_log.insert(0, multi_window)


def pause():
    print('pause')


def back():
    window_log.pop(0)


def join():
    score = GameClient(window, client_connect()).loop()
    game_over_window.widgets.append(Text('score: ' + str(score), windowWidth/2, 200))
    window_log.insert(0, game_over_window)


def create():
    score = GameServer(window, server_connect()).loop()
    game_over_window.widgets.append(Text('score: ' + str(score), windowWidth/2, 200))
    window_log.insert(0, game_over_window)


def home():
    window_log.insert(0, starting_window)


background = pg.Surface((windowWidth, windowHeight))
background.fill((40, 40, 50))

starting_window = Window(windowWidth, windowHeight, background)
starting_window.widgets.append(Button(windowWidth / 2, 200, 200, 50, play_single, img=button_img, text='Single'))
starting_window.widgets.append(Button(windowWidth / 2, 300, 200, 50, play_multi, img=button_img, text='Multi'))
starting_window.widgets.append(Button(windowWidth / 2, 400, 200, 50, stop, img=button_img, text='quit'))

multi_window = Window(windowWidth, windowHeight, background)
multi_window.widgets.append(Button(windowWidth / 2, 200, 200, 50, join, img=button_img, text='Join'))
multi_window.widgets.append(Button(windowWidth / 2, 300, 200, 50, create, img=button_img, text='Create'))
multi_window.widgets.append(Button(windowWidth / 2, 400, 200, 50, back, img=button_img, text='back'))

game_over_window = Window(windowWidth, windowHeight, background)
game_over_window.widgets.append(Text('Game Over!', windowWidth / 2, 100))
game_over_window.widgets.append(Button(windowWidth / 2, 300, 200, 50, home, img=button_img, text='Home'))


window_log.insert(0, starting_window)


def server_connect():
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
    s.bind(('', 5000))
    s.listen(1)
    sock, adress = s.accept()

    return sock


def client_connect():
    bs = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    bs.bind(('', 5555))

    data, adress = bs.recvfrom(1024)
    bs.sendto(b'hey', adress)

    adress = adress[0], 5000

    s = socket.socket()
    s.connect(adress)

    return s


while running:
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            window_log[0].collision(event.pos[0], event.pos[1])

    window_log[0].draw(window)
    pg.display.update()

pg.quit()
