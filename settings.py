import pygame as pg

pg.font.init()

windowWidth = 700
windowHeight = 500
mapSize = 4000
allSprites = pg.sprite.Group()
bullets = pg.sprite.Group()
particles = pg.sprite.Group()
font = pg.font.Font(pg.font.get_default_font(), 30)
fps = 60
