import math

import pygame

UNKNOWN = 0
LEFT = 1
RIGHT = 2
TOP = 3
BOTTOM =4

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

        if not xin:
            xin = self.right >= other.left and self.left <= other.right
        if not yin:
            yin = self.bottom >= other.top and self.top <= other.bottom
        if xout:
            xin = False
        if yout:
            yin = False
        
        dt = 0

        if xin:
            if yin:
                return True, dt, UNKNOWN
            else:
                side = UNKNOWN
                t_yin = float('+inf')
                t_xout = float('+inf')
                if self.bottom < other.top:
                    side = BOTTOM
                    if ay > 0:
                        t_yin = (-v0y + math.sqrt(v0y**2 - 2*ay*(self.bottom - other.top)))/ay
                    elif v0y > 0:
                        if ay == 0:
                            t_yin = -(self.bottom - other.top)/v0y
                        else:
                            disc = v0y**2 - 2*ay*(self.bottom - other.top)
                            if disc <= 0:
                                return False, None, UNKNOWN
                            t_yin = (-v0y + math.sqrt(disc))/ay
                else:
                    side = TOP
                    if ay < 0:
                        t_yin = (-v0y - math.sqrt(v0y**2 - 2*ay*(self.top - other.bottom)))/ay
                    elif v0y < 0:
                        if ay == 0:
                            t_yin = -(self.top - other.bottom)/v0y
                        else:
                            disc = v0y**2 - 2*ay*(self.top - other.bottom)
                            if disc <= 0:
                                return False, None, UNKNOWN
                            t_yin = (-v0y - math.sqrt(disc))/ay
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

                if t_yin < t_xout:
                    return True, t_yin, side
                elif t_xout < limit:
                    if n > 10:
                        print("Warning: too many collision iterations, breaking out from vertical")
                    return self.next_contact(other, limit, t_xout, n=n+1, xout=True)
        else:
            if yin:
                side = UNKNOWN
                t_xin = float('+inf')
                t_yout = float('+inf')
                if self.right < other.left:
                    side = RIGHT
                    if ax > 0:
                        t_xin = (-v0x + math.sqrt(v0x**2 - 2*ax*(self.right - other.left)))/ax
                    elif v0x > 0:
                        if ax == 0:
                            t_xin = -(self.right - other.left)/v0x
                        else:
                            disc = v0x**2 - 2*ax*(self.right - other.left)
                            if disc <= 0:
                                return False, None, UNKNOWN
                            t_xin = (-v0x + math.sqrt(disc))/ax
                else:
                    side = LEFT
                    if ax < 0:
                        t_xin = (-v0x - math.sqrt(v0x**2 - 2*ax*(self.left - other.right)))/ax
                    elif v0x < 0:
                        if ax == 0:
                            t_xin = -(self.left - other.right)/v0y
                        else:
                            disc = v0x**2 - 2*ax*(self.left - other.right)
                            if disc <= 0:
                                return False, None, UNKNOWN
                            t_xin = (-v0x - math.sqrt(disc))/ax
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

                if t_xin < t_yout:
                    return True, t_xin, side
                elif t_yout < limit:
                    if n > 10:
                        print("Warning: too many collision iterations, breaking out from horizontal")
                    return self.next_contact(other, limit, t_yout, n=n+1, yout=True)
            else:
                t_xin = float('+inf')
                t_yin = float('+inf')
                if self.bottom <= other.top:
                    if ay > 0:
                        t_yin = (-v0y + math.sqrt(v0y**2 - 2*ay*(self.bottom - other.top)))/ay
                    elif v0y > 0:
                        if ay == 0:
                            t_yin = -(self.bottom - other.top)/v0y
                        else:
                            disc = v0y**2 - 2*ay*(self.bottom - other.top)
                            if disc <= 0:
                                return False, None, UNKNOWN
                            t_yin = (-v0y + math.sqrt(disc))/ay
                else:
                    if ay < 0:
                        t_yin = (-v0y - math.sqrt(v0y**2 - 2*ay*(self.top - other.bottom)))/ay
                    elif v0y < 0:
                        if ay == 0:
                            t_yin = -(self.top - other.bottom)/v0y
                        else:
                            disc = v0y**2 - 2*ay*(self.top - other.bottom)
                            if disc <= 0:
                                return False, None, UNKNOWN
                            t_yin = (-v0y - math.sqrt(disc))/ay
                if self.right <= other.left:
                    if ax > 0:
                        t_xin = (-v0x + math.sqrt(v0x**2 - 2*ax*(self.right - other.left)))/ax
                    elif v0x > 0:
                        if ax == 0:
                            t_xin = -(self.right - other.left)/v0x
                        else:
                            disc = v0x**2 - 2*ax*(self.right - other.left)
                            if disc <= 0:
                                return False, None, UNKNOWN
                            t_xin = (-v0x + math.sqrt(disc))/ax
                else:
                    if ax < 0:
                        t_xin = (-v0x - math.sqrt(v0x**2 - 2*ax*(self.left - other.right)))/ax
                    elif v0x < 0:
                        if ax == 0:
                            t_xin = -(self.left - other.right)/v0y
                        else:
                            disc = v0x**2 - 2*ax*(self.left - other.right)
                            if disc <= 0:
                                return False, None, UNKNOWN
                            t_xin = (-v0x - math.sqrt(disc))/ax
                t_next = min(t_yin, t_xin)
                if t_next < limit and n < 10:
                    return self.next_contact(other, limit, t_next, n=n+1, xin=(t_next==t_xin), yin=(t_next==t_yin))
                else:
                    if n > 10:
                        print("Warning: too many collision iterations, breaking out from off-axis")
                    return False, None, UNKNOWN
        return False, None, UNKNOWN

    def contact_end(self, other, side):
        ax = self.acc[0] - other.acc[0]
        ay = self.acc[1] - other.acc[1]

        v0x = self.vel[0] - other.vel[0]
        v0y = self.vel[1] - other.vel[1]

        t_xout = float('+inf')
        t_yout = float('+inf')

        if side == TOP or side == BOTTOM:
            if side == TOP:
                if v0y > 0:
                    return 0
                elif ay > 0:
                    t_yout = -v0y/ay
            elif side == BOTTOM:
                if v0y < 0:
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
                if v0x > 0:
                    return 0
                elif ax > 0:
                    t_xout = -v0x/ax
            elif side == RIGHT:
                if v0x < 0:
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
        #print(self.vel[1]*dt, self.pos[1])
