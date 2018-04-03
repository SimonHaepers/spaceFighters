import pygame as pg

pg.font.init()

windowWidth = 700
windowHeight = 500
mapSize = 20000
allSprites = pg.sprite.Group()
particles = pg.sprite.Group()
explosions = []
fps = 60
window = pg.display.set_mode((windowWidth, windowHeight))
