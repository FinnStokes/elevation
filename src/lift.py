import pygame

import physics

class Lift(pygame.sprite.Sprite):
    """A wall or floor that is impassable to entities."""

    def __init__(self, image, (x, y0, y1), vy):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.rect.midbottom = (x, y1)
        self.ay = 150
        self.target = y1
        self.vy = vy
        self.y0 = y0
        self.y1 = y1
        self.body = physics.Body(self.rect.topleft, (self.rect.width, self.rect.height))

    def update(self, dt):
        self.body.update(dt)
        self.rect.topleft = self.body.pos
        # dy = self.target - self.rect.bottom
        
        # if abs(self.body.vel[1]) > self.vy:
        #     a = min(self.ay, (abs(self.body.vel[1]) - self.vy)/dt)
        #     self.body.acc = (0, -a * self.body.vel[1] / abs(self.body.vel[1]))
        # elif self.body.vel[1]*dy < 0:
        #     a = min(self.ay, abs(self.body.vel[1])/dt)
        #     self.body.acc = (0, a * dy / abs(dy))
        # elif dy != 0:
        #     if abs(self.body.vel[1]**2 / (2*dy)) < self.ay:
        #         a = min(self.ay, (self.vy - abs(self.body.vel[1])) / dt)
        #     else:
        #         a = -min(self.ay, abs(self.body.vel[1]**2 / (2*dy)), abs(self.body.vel[1]/dt))
        #     self.body.acc = (0, a * dy / abs(dy))
        # else:
        #     if self.body.vel[1] != 0:
        #         a = min(self.ay, abs(self.body.vel[1])/dt)
        #         self.body.acc = (0, -a * self.body.vel[1] / abs(self.body.vel[1]))
        #     else:
        #         self.body.acc = (0, 0)

        if self.rect.bottom < self.y0:
            self.rect.bottom = self.y0
            self.body.pos = self.rect.topleft
            if self.body.vel[1] < 0:
                self.body.vel = (0,0)
        if self.rect.bottom > self.y1:
            self.rect.bottom = self.y1
            self.body.pos = self.rect.topleft
            if self.body.vel[1] > 0:
                self.body.vel = (0,0)

    def up(self):
        self.body.vel = (0, -self.vy)
        # self.target = self.y0

    def down(self):
        self.body.vel = (0, self.vy)
        # self.target = self.y1
