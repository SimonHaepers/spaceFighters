import pygame as pg

pg.font.init()
font = pg.font.Font('png/kenvector_future.ttf', 20)


class Button:
    def __init__(self, x, y, w, h, func, img=None, text=None):
        self.rect = pg.Rect(x-w/2, y-h/2, w, h)

        if img:
            self.image = img.copy()
            self.rect.w, self.rect.h = img.get_size()
        else:
            self.image = pg.Surface((w, h), pg.SRCALPHA)

        if text:
            text_img = font.render(text, True, (0, 0, 0))
            self.image.blit(text_img, ((w - text_img.get_width()) / 2, (h - text_img.get_height()) / 2))

        self.func = func

    def collision(self, x, y):
        if self.rect.collidepoint(x, y):
            self.func()

    def draw(self, w):
        w.blit(self.image, (self.rect.x, self.rect.y))


class Window:
    def __init__(self, w, h, background=None):
        self.width = w
        self.height = h

        if background:
            self.bg = background
        else:
            self.bg = pg.Surface((self.width, self.height), pg.SRCALPHA)

        self.widgets = []

    def draw(self, w):
        w.blit(self.bg, (0, 0))

        for widget in self.widgets:
            widget.draw(w)

    def collision(self, x, y):
        for widget in self.widgets:
            widget.collision(x, y)
