import pygame

import physics

class Lift(pygame.sprite.Sprite):
    """An wall or floor that is impassable to entities."""

    def __init__(self, image, (x, y0, y1), vy):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.rect.midbottom = (x, y1)
        self.vy = vy
        self.y0 = y0
        self.y1 = y1
        self.body = physics.Body(self.rect.topleft, (self.rect.width, self.rect.height))

    def update(self, dt):
        self.body.update(dt)
        self.rect.topleft = self.body.pos
        if self.rect.bottom < self.y0:
            self.rect.bottom = self.y0
            self.body.pos = self.rect.topleft
            if self.body.vel[0] < 0:
                self.body.vel = (0,0)
        if self.rect.bottom > self.y1:
            self.rect.bottom = self.y1
            self.body.pos = self.rect.topleft
            if self.body.vel[0] > 0:
                self.body.vel = (0,0)

    def up(self):
        self.body.vel = (0, -self.vy)

    def down(self):
        self.body.vel = (0, self.vy)
