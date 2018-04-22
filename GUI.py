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
            if isinstance(widget, Button):
                widget.collision(x, y)


class Text:
    def __init__(self, txt, x, y):
        self.image = font.render(txt, True, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = x, y

    def draw(self, w):
        w.blit(self.image, (self.rect.x, self.rect.y))


class LoadingAnimation:
    def __init__(self, x, y):
        self.index = 0
        img = pg.image.load('png/loading.png')
        self.images = []

        for i in range(8):
            cropped = pg.Surface((64, 64), pg.SRCALPHA)
            cropped.blit(img, (-i*64, 0))
            self.images.append(cropped)

        self.rect = pg.Rect(x - 32, y - 32, 64, 64)

    def draw(self, w):
        if int(self.index) == 8:
            self.index = 0
        w.blit(self.images[int(self.index)], (self.rect.x, self.rect.y))
        self.index += 0.05

