import itertools
import math

import pygame
from pygame.locals import *
from pygame import gfxdraw

import physics

class Entity(pygame.sprite.Sprite):
    """An entity that moves around the level."""

    def __init__(self, image, size, (x, y), (vx, vy)):
        pygame.sprite.Sprite.__init__(self)
        self.left_img = image
        self.right_img = pygame.transform.flip(image, True, False)
        self.image = self.left_img
        self.rect = image.get_rect()
        self.rect.midbottom = (x, y)
        self.colliderect = pygame.Rect((0,0), size)
        self.colliderect.midbottom = self.rect.midbottom
        self.gravity = 300
        self.target_vel = (vx, vy)
        self.body = physics.Body(self.colliderect.topleft, size, (vx, vy), (0, self.gravity))
        self.contact = []
        #self.level = level

    def moveto(self, pos):
        self.rect.midbottom = pos
        self.colliderect.midbottom = self.rect.midbottom
        self.body.pos = self.colliderect.topleft

    def _on_collide(self, body, time, side):
        def callback():
            self.collide(body, side)
            # print("Collide {} on {} at {}".format(body, side, self.body.pos))
            self.contact.append((body,side))
        return callback

    def _on_uncollide(self, body, time, side):
        def callback():
            # print("Uncollide {} on {} at {}".format(body, side, self.body.pos))
            self.contact = [x for x in self.contact if x[0] != body]
            self.uncollide(body, side)
        return callback

    def collide(self, body, side):
        if side == physics.LEFT and self.target_vel[0] < 0:
            # print("collideleft")
            self.target_vel = (-self.target_vel[0], self.target_vel[1])
        elif side == physics.RIGHT and self.target_vel[0] > 0:
            # print("collideright")
            self.target_vel = (-self.target_vel[0], self.target_vel[1])
        # if side == physics.LEFT and self.body.vel[0] < 0:
        #     self.body.vel = (body.vel[0], self.body.vel[1])
        # if side == physics.RIGHT and self.body.vel[0] > 0:
        #     self.body.vel = (body.vel[0], self.body.vel[1])
        # if side == physics.TOP and self.body.vel[1] < 0:
        #     self.body.vel = (self.body.vel[0], body.vel[1])
        # if side == physics.BOTTOM and self.body.vel[1] > 0:
        #     self.body.vel = (self.body.vel[0], body.vel[1])
        #     self.body.acc = (0, 0)
        #     #print(self.body.vel[1])

    def uncollide(self, body, side):
        pass
        # if side == physics.BOTTOM:
        #     for c in self.contact:
        #         if c[1] == physics.BOTTOM:
        #             return
        #     self.body.acc = (0, self.gravity)
        # elif side == physics.RIGHT:
        #     self.body.vel = (self.target_vel[0], self.body.vel[1])

    def update(self, dt, bodies, to=0, n=0):
        #print("upd", dt)
        self.body.vel = (self.target_vel[0], self.body.vel[1])
        self.body.acc = (0, self.gravity)
        # print(self.body.vel)
        # print(self.body.acc)
        top = self.body.top
        left = self.body.left
        force = {}
        for body, side in self.contact:
            ax = self.body.acc[0] - body.acc[0]
            ay = self.body.acc[1] - body.acc[1]
            v0x = self.body.vel[0] - body.vel[0]
            v0y = self.body.vel[1] - body.vel[1]
            if side == physics.LEFT:
                self.body.left = body.right
                force[side] = body
                if physics.RIGHT in force:
                    if force[physics.RIGHT].vel[0] != body.vel[0] or force[physics.RIGHT].acc[0] != body.acc[0]:
                        self.contact = [x for x in self.contact if x[0] not in [b for b in (body, force[physics.RIGHT]) if b.vel[0] != 0 or b.acc[0] != 0]]
                        self.body.left = left
                        self.body.vel = (0, self.body.vel[1])
                        self.body.acc = (0, self.body.acc[1])
                        continue
                if v0x < 0:
                    self.body.vel = (body.vel[0], self.body.vel[1])
                if v0x <= 0 and ax < 0:
                    self.body.acc = (body.acc[0], self.body.acc[1])
            elif side == physics.RIGHT:
                self.body.right = body.left
                force[side] = body
                if physics.LEFT in force:
                    if force[physics.LEFT].vel[0] != body.vel[0] or force[physics.LEFT].acc[0] != body.acc[0]:
                        self.contact = [x for x in self.contact if x[0] not in [b for b in (body, force[physics.LEFT]) if b.vel[0] != 0 or b.acc[0] != 0]]
                        self.body.left = left
                        self.body.vel = (0, self.body.vel[1])
                        self.body.acc = (0, self.body.acc[1])
                        continue
                force[side] = body
                force[side] = body
                if v0x > 0:
                    self.body.vel = (body.vel[0], self.body.vel[1])
                if v0x >= 0 and ax > 0:
                    self.body.acc = (body.acc[0], self.body.acc[1])
            elif side == physics.TOP:
                self.body.top = body.bottom
                force[side] = body
                if physics.BOTTOM in force:
                    if force[physics.BOTTOM].vel[1] != body.vel[1] or force[physics.BOTTOM].acc[1] != body.acc[1]:
                        self.contact = [x for x in self.contact if x[0] not in [b for b in (body, force[physics.BOTTOM]) if b.vel[1] != 0 or b.acc[1] != 0]]
                        self.body.top = top
                        self.body.vel = (self.body.vel[0], 0)
                        self.body.acc = (self.body.acc[0], 0)
                        continue
                if v0y < 0:
                    self.body.vel = (self.body.vel[0], body.vel[1])
                if v0y <= 0 and ay < 0:
                    self.body.acc = (self.body.acc[0], body.acc[1])
            elif side == physics.BOTTOM:
                self.body.bottom = body.top
                force[side] = body
                if physics.TOP in force:
                    if force[physics.TOP].vel[1] != body.vel[1] or force[physics.TOP].acc[1] != body.acc[1]:
                        self.contact = [x for x in self.contact if x[0] not in [b for b in (body, force[physics.TOP]) if b.vel[1] != 0 or b.acc[1] != 0]]
                        self.body.top = top
                        self.body.vel = (self.body.vel[0], 0)
                        self.body.acc = (self.body.acc[0], 0)
                        continue
                if v0y > 0:
                    self.body.vel = (self.body.vel[0], body.vel[1])
                if v0y >= 0 and ay > 0:
                    self.body.acc = (self.body.acc[0], body.acc[1])
        # if physics.LEFT in force and physics.RIGHT in force:
        #     self.body.left = left
        #     self.body.vel = (0, self.body.vel[1])
        #     self.body.acc = (0, self.body.acc[1])
        #     #print("Warning: horizontal crush")
        # if physics.TOP in force and physics.BOTTOM in force:
        #     print([(b, b.vel, b.acc) for b in (force[physics.TOP], force[physics.BOTTOM]) if b.vel[1] != 0 or b.acc[1] != 0])
        #     self.body.top = top
        #     self.body.vel = (self.body.vel[0], 0)
        #     self.body.acc = (self.body.acc[0], 0)
        #     #print("Warning: vertical crush")
        t_min = dt
        action = False
        for body in self.body.proximal(bodies, dt):
            # print(body.left, body.top, body.right, body.bottom)
            if body not in (c[0] for c in self.contact):
                t, side = self.body.next_contact(body.offset(to))
                if t < t_min:
                    t_min = t
                    action = self._on_collide(body, t, side)
                    # print("collide", t, body)
        for body, side in self.contact:
            t = self.body.contact_end(body.offset(to), side)
            if t < t_min:
                t_min = t
                action = self._on_uncollide(body, t, side)
                # print("uncollide", t, body)
        # print("update", t_min, self.body.vel, self.body.acc)
        self.body.update(t_min)
        if action:
            action()
            # print("recurse {}".format(n))
            if n<20:
                self.update(dt - t_min, bodies, to=to+t_min, n=n+1)
                return
            else:
                print("Warning: too many iteration steps in collisions")
        self.body.update(dt - t_min)
        self.colliderect.topleft = self.body.pos
        self.rect.midbottom = self.colliderect.midbottom
        if self.body.vel[0] > 0:
            self.image = self.left_img
        elif self.body.vel[0] < 0:
            self.image = self.right_img
