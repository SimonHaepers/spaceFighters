import pygame as pg

pg.font.init()

windowWidth = 1000
windowHeight = 700
mapSize = 6000
allSprites = pg.sprite.Group()
bullets = pg.sprite.Group()
particles = pg.sprite.Group()
explosions = []
font = pg.font.Font(pg.font.get_default_font(), 30)
fps = 60
window = pg.display.set_mode((windowWidth, windowHeight), pg.NOFRAME)
