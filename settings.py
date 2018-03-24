import pygame as pg

pg.font.init()

windowWidth = 1366
windowHeight = 768
mapSize = 4000
allSprites = pg.sprite.Group()
bullets = pg.sprite.Group()
particles = pg.sprite.Group()
explosions = []
font = pg.font.Font(pg.font.get_default_font(), 30)
fps = 60
