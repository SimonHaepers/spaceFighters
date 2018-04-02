import pygame as pg

pg.font.init()

windowWidth = 1366
windowHeight = 768
mapSize = 20000
allSprites = pg.sprite.Group()
bullets = pg.sprite.Group()
particles = pg.sprite.Group()
explosions = []
font = pg.font.Font('png/kenvector_future.ttf', 30)
fps = 60
window = pg.display.set_mode((windowWidth, windowHeight), pg.FULLSCREEN)
