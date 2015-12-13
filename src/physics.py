import math

import pygame

UNKNOWN = 0
LEFT = 1
RIGHT = 2
TOP = 3
BOTTOM = 4

class Body():
    def __init__(self, pos, size, vel=(0,0), acc=(0,0)):
        self.pos = pos
        self.size = size
        self.vel = vel
        self.acc = acc

    @property
    def left(self):
        return self.pos[0]
        
    @property
    def right(self):
        return self.pos[0] + self.size[0]
        
    @property
    def top(self):
        return self.pos[1]
        
    @property
    def bottom(self):
        return self.pos[1] + self.size[1]

    @left.setter
    def left(self, value):
        self.pos[0] = value
        
    @right.setter
    def right(self, value):
        self.pos[0] = value - self.size[0]
        
    @top.setter
    def top(self, value):
        self.pos[1] = value
        
    @bottom.setter
    def bottom(self, value):
        self.pos[1] = value - self.size[1]

    def bounding_box(self, dt):
        if self.acc[0] != 0:
            dx = self.vel[0]*dt + self.acc[0]*(dt**2)/2
            x_cusp = -self.vel[0]/self.acc[0]
            if x_cusp > 0 and x_cusp < dt:
                dx_cusp = x_cusp*self.vel[0]/2.0
                if dx_cusp < 0:
                    left = self.left + dx_cusp
                    right = max(self.right, self.right + dx)
                else:
                    left = max(self.left, self.left + dx)
                    right = self.right + dx_cusp
            else:
                if dx < 0:
                    left = self.left + dx
                    right = self.right
                else:
                    left = self.left
                    right = self.right + dx
        else:
            dx = self.vel[0]*dt
            if dx < 0:
                left = self.left + dx
                right = self.right
            else:
                left = self.left
                right = self.right + dx
        if self.acc[1] != 0:
            dy = self.vel[1]*dt + self.acc[1]*(dt**2)/2
            y_cusp = -self.vel[1]/self.acc[1]
            if y_cusp > 0 and y_cusp < dt:
                dy_cusp = y_cusp*self.vel[1]/2.0
                if dy_cusp < 0:
                    top = self.top + dy_cusp
                    bottom = max(self.bottom, self.bottom + dy)
                else:
                    top = max(self.top, self.top + dy)
                    bottom = self.bottom + dy_cusp
            else:
                if dy < 0:
                    top = self.top + dy
                    bottom = self.bottom
                else:
                    top = self.top
                    bottom = self.bottom + dy
        else:
            dy = self.vel[1]*dt
            if dy < 0:
                top = self.top + dy
                bottom = self.bottom
            else:
                top = self.top
                bottom = self.bottom + dy
        
        return left, right, top, bottom

    def proximal(self, bodies, dt):
        left, right, top, bottom = self.bounding_box(dt)
        for b in bodies:
            b_left, b_right, b_top, b_bottom = self.bounding_box(dt)
            if right >= b_left and left <= b_right and bottom >= b_top and top <= b_bottom:
                yield b
    
    def next_contact(self, other, limit, dt=0, n=0, xin=False, yin=False, xout=False, yout=False):
        ax = self.acc[0] - other.acc[0]
        ay = self.acc[1] - other.acc[1]

        v0x = self.vel[0] - other.vel[0]
        v0y = self.vel[1] - other.vel[1]

        inf = float('+inf')

        if ax == 0:
            if v0x == 0:
                if self.right > other.left and self.left < other.right:
                    xin =[(-inf, inf, UNKNOWN)]
                else:
                    xin = []
            elif v0x > 0:
                xin = [(-(self.right - other.left) * 1.0 / v0x, -(self.left - other.right) * 1.0 / v0x, RIGHT)]
            else:
                xin = [(-(self.left - other.right) * 1.0 / v0x, -(self.right - other.left) * 1.0 / v0x, LEFT)]
        else:
            ldesc = v0x**2 - 2*ax*(self.left - other.right)
            rdesc = v0x**2 - 2*ax*(self.right - other.left)
            if ax > 0:
                if rdesc <= 0:
                    if ldesc <= 0:
                        xin = []
                    else:
                        sqrt_ldesc = math.sqrt(ldesc)
                        xin = [((-v0x - sqrt_ldesc)/ax, (-v0x + sqrt_ldesc)/ax, LEFT)]
                else:
                    sqrt_ldesc = math.sqrt(ldesc)
                    sqrt_rdesc = math.sqrt(rdesc)
                    xin = [((-v0x - sqrt_ldesc)/ax, (-v0x - sqrt_rdesc)/ax, LEFT), ((-v0x + sqrt_rdesc)/ax, (-v0x + sqrt_ldesc)/ax, RIGHT)]
            else:
                if ldesc <= 0:
                    if rdesc <= 0:
                        xin = []
                    else:
                        sqrt_rdesc = math.sqrt(rdesc)
                        xin = [((-v0x + sqrt_rdesc)/ax, (-v0x - sqrt_rdesc)/ax, RIGHT)]
                else:
                    sqrt_ldesc = math.sqrt(ldesc)
                    sqrt_rdesc = math.sqrt(rdesc)
                    xin = [((-v0x + sqrt_rdesc)/ax, (-v0x + sqrt_ldesc)/ax, RIGHT), ((-v0x - sqrt_ldesc)/ax, (-v0x - sqrt_rdesc)/ax, LEFT)]

        if ay == 0:
            if v0y == 0:
                if self.bottom > other.top and self.top < other.bottom:
                    yin =[(-inf, inf, UNKNOWN)]
                else:
                    yin = []
            elif v0y > 0:
                yin = [(-(self.bottom - other.top) * 1.0 / v0y, -(self.top - other.bottom) * 1.0 / v0y, BOTTOM)]
            else:
                yin = [(-(self.top - other.bottom) * 1.0 / v0y, -(self.bottom - other.top) * 1.0 / v0y, TOP)]
        else:
            tdesc = v0y**2 - 2*ay*(self.top - other.bottom)
            bdesc = v0y**2 - 2*ay*(self.bottom - other.top)
            if ay > 0:
                if bdesc <= 0:
                    if tdesc <= 0:
                        yin = []
                    else:
                        sqrt_tdesc = math.sqrt(tdesc)
                        yin = [((-v0y - sqrt_tdesc)/ay, (-v0y + sqrt_tdesc)/ay, TOP)]
                else:
                    sqrt_tdesc = math.sqrt(tdesc)
                    sqrt_bdesc = math.sqrt(bdesc)
                    yin = [((-v0y - sqrt_tdesc)/ay, (-v0y - sqrt_bdesc)/ay, TOP), ((-v0y + sqrt_bdesc)/ay, (-v0y + sqrt_tdesc)/ay, BOTTOM)]
            else:
                if tdesc <= 0:
                    if bdesc <= 0:
                        yin = []
                    else:
                        sqrt_bdesc = math.sqrt(bdesc)
                        yin = [((-v0y + sqrt_bdesc)/ay, (-v0y - sqrt_bdesc)/ay, BOTTOM)]
                else:
                    sqrt_tdesc = math.sqrt(tdesc)
                    sqrt_bdesc = math.sqrt(bdesc)
                    yin = [((-v0y + sqrt_bdesc)/ay, (-v0y + sqrt_tdesc)/ay, BOTTOM), ((-v0y - sqrt_tdesc)/ay, (-v0y - sqrt_bdesc)/ay, TOP)]

        for xwin in xin:
            if xwin[1] <= 0:
                continue
            for ywin in yin:
                if ywin[1] <= 0:
                    continue
                if ywin[0] > xwin[0]:
                    t = ywin[0]
                    side = ywin[2]
                else:
                    t = xwin[0]
                    side = xwin[2]
                if min(xwin[1], ywin[1]) > t:
                    return max(t, 0), side

        return inf, UNKNOWN
                    
    def contact_end(self, other, side):
        ax = self.acc[0] - other.acc[0]
        ay = self.acc[1] - other.acc[1]

        v0x = self.vel[0] - other.vel[0]
        v0y = self.vel[1] - other.vel[1]

        t_xout = float('+inf')
        t_yout = float('+inf')

        if side == TOP or side == BOTTOM:
            if side == TOP:
                if v0y > 0:# or self.top > other.bottom:
                    return 0
                elif ay > 0:
                    t_yout = -v0y/ay
            elif side == BOTTOM:
                if v0y < 0:# or self.bottom < other.top:
                    return 0
                elif ay < 0:
                    t_yout = -v0y/ay
            if ax == 0:
                if v0x > 0:
                    t_xout = -(self.left - other.right)/v0x
                elif v0x < 0:
                    t_xout = -(self.right - other.left)/v0x
            elif ax > 0:
                t_xout = (-v0x + math.sqrt(v0x**2 - 2*ax*(self.left - other.right)))/ax
                if v0x < 0:
                    disc = v0x**2 - 2*ax*(self.right - other.left)
                    if disc > 0:
                        t_xout = min(t_xout, (-v0x - math.sqrt(disc))/ay)
            else:
                t_xout = (-v0x - math.sqrt(v0x**2 - 2*ax*(self.right - other.left)))/ax
                if v0x > 0:
                    disc = v0x**2 - 2*ax*(self.left - other.right)
                    if disc > 0:
                        t_xout = min(t_xout, (-v0x + math.sqrt(disc))/ax)
            return min(t_xout,t_yout)
        elif side == LEFT or side == RIGHT:
            if side == LEFT:
                if v0x > 0:# or self.left > other.left:
                    return 0
                elif ax > 0:
                    t_xout = -v0x/ax
            elif side == RIGHT:
                if v0x < 0:# or self.right > other.right:
                    return 0
                elif ax < 0:
                    t_xout = -v0x/ax
            if ay == 0:
                if v0y > 0:
                    t_yout = -(self.top - other.bottom)/v0y
                elif v0y < 0:
                    t_yout = -(self.bottom - other.top)/v0y
            elif ay > 0:
                t_yout = (-v0y + math.sqrt(v0y**2 - 2*ay*(self.top - other.bottom)))/ay
                if v0y < 0:
                    disc = v0y**2 - 2*ay*(self.bottom - other.top)
                    if disc > 0:
                        t_yout = min(t_yout, (-v0y - math.sqrt(disc))/ay)
            else:
                t_yout = (-v0y - math.sqrt(v0y**2 - 2*ay*(self.bottom - other.top)))/ay
                if v0x > 0:
                    disc = v0y**2 - 2*ay*(self.top - other.bottom)
                    if disc > 0:
                        t_yout = min(t_yout, (-v0y + math.sqrt(disc))/ay)
            if t_xout < 0:
                return t_yout
            else:
                return min(t_xout, t_yout)
        else:
            return 0

    def update(self, dt):
        self.pos = (self.pos[0] + self.vel[0]*dt + self.acc[0]*(dt**2)/2, self.pos[1] + self.vel[1]*dt + self.acc[1]*(dt**2)/2)
        self.vel = (self.vel[0] + self.acc[0]*dt, self.vel[1] + self.acc[1]*dt)
        print("phys_update", self.acc[1], self.vel[1], self.bottom, dt)
