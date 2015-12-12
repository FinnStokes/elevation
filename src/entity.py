import itertools
import math

import pygame
from pygame.locals import *
from pygame import gfxdraw

import physics

bodies = [physics.Body((0, 800), (1000, 0)), physics.Body((1000, 200), (10, 600))]

class Entity(pygame.sprite.Sprite):
    """An entity that moves around the level."""

    def __init__(self, image, x, y, vx, vy):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.rect.topleft = (x, y)
        self.gravity = 300
        self.body = physics.Body((x, y), (self.rect.width, self.rect.height), (vx, vy), (0, self.gravity))
        self.contact = []
        #self.level = level

    def _on_collide(self, body, time, side):
        self.collide(body, side)
        #print("Collide {} on {}".format(body, side))
        self.contact.append((body,side))

    def _on_uncollide(self, body, time, side):
        #print("Uncollide {}".format(body))
        self.contact = [x for x in self.contact if x[0] != body]
        self.uncollide(body, side)

    def collide(self, body, side):
        if side == physics.LEFT and self.body.vel[0] < 0:
            self.body.vel = (0, self.body.vel[1])
        if side == physics.RIGHT and self.body.vel[0] > 0:
            self.body.vel = (0, self.body.vel[1])
        if side == physics.TOP and self.body.vel[0] < 0:
            self.body.vel = (self.body.vel[0], 0)
        if side == physics.BOTTOM and self.body.vel[0] > 0:
            self.body.vel = (self.body.vel[0], 0)
            self.body.acc = (0, 0)
            #print(self.body.vel[1])

    def uncollide(self, body, side):
        if side == physics.BOTTOM:
            for c in self.contact:
                if c[1] == physics.BOTTOM:
                    return
            self.body.acc = (0, self.gravity)

    def update(self, dt):
        #print("update", dt)
        # for body, side in self.contact:
        #     if side == physics.LEFT:
        #         if self.body.left < body.right:
        #             self.body.left = body.right
        #     elif side == physics.RIGHT:
        #         if self.body.right > body.left:
        #             self.body.right = body.left
        #     elif side == physics.TOP:
        #         if self.body.top < body.bottom:
        #             self.body.top = body.bottom
        #     elif side == physics.BOTTOM:
        #         #print(body.top)
        #         if self.body.bottom > body.top:
        #             #print(body.top)
        #             self.body.bottom = body.top
        t_min = dt
        action = False
        for body in self.body.proximal(bodies, dt):
            #print(body.left, body.top, body.right, body.bottom)
            if body not in (c[0] for c in self.contact):
                ok, t, side = self.body.next_contact(body, dt)
                if ok and t < t_min:
                    #print("b", body)
                    t_min = t
                    action = self._on_collide(body, t, side)
        for body, side in self.contact:
            t = self.body.contact_end(body, side)
            if t < t_min:
                t_min = t
                action = self._on_uncollide(body, t, side)
        self.body.update(t_min)
        if action:
            action()
            #print("recurse")
            self.update(dt - t_min)
        else:
            self.rect.topleft = self.body.pos
