import os

import pygame
from pygame.locals import *
import pytmx
import pytmx.util_pygame as pytmxutil

import physics

class Level(object):
    """A tile-based level"""

    def __init__(self, filename):
        self.data = pytmxutil.load_pygame(filename)
        self.surface = pygame.Surface((self.data.width*self.data.tilewidth, self.data.height*self.data.tileheight))
        if "Timelimit" in self.data.properties:
            self.time_limit = float(self.data.properties["Timelimit"])
        else:
            self.time_limit = None
        self.refresh(self.surface.get_rect())

    def refresh(self, rect):
        self.walls = []
        self.goals = []
        self.spawn = []
        self.shafts = []
        self.buttons = []
        self.spikes = []
        self.groups = {}
        self.openDoors = pygame.sprite.Group()
        
        surface_blit = self.surface.blit
        tw = self.data.tilewidth
        th = self.data.tileheight
        top = rect.top
        left = rect.left

        if self.data.background_color:
            self.surface.fill(pygame.Color(self.data.background_color))

        for layer in self.data.visible_tile_layers:
            # iterate over the tiles in the layer
            inshaft = []
            for x, y, image in self.data.layers[layer].tiles():
                surface_blit(image, (x * tw - left, y * th - top))
                properties = self.data.get_tile_properties(x, y, layer)
                if properties:
                    wall = None
                    if "Floor" in properties and properties["Floor"] == "True":
                        floor_height = int(self.data.get_tileset_from_gid(self.data.get_tile_gid(x, y, layer)).properties["Floorheight"])
                        fx = x * tw - left
                        fy = y * th - top + th - floor_height
                        self.walls.append(physics.Body((fx, fy), (tw, floor_height)))
                    if "Wall" in properties and properties["Wall"] == "True":
                        wall_width = int(self.data.get_tileset_from_gid(self.data.get_tile_gid(x, y, layer)).properties["Wallwidth"])
                        wall_pos = int(properties["Wallpos"])
                        fx = x * tw - left + wall_pos
                        fy = y * th - top
                        wall = physics.Body((fx, fy), (wall_width, th))
                        self.walls.append(wall)
                    if "Spawn" in properties and properties["Spawn"] == "True":
                        floor_height = int(self.data.get_tileset_from_gid(self.data.get_tile_gid(x, y, layer)).properties["Floorheight"])
                        self.spawn.append((x * tw - left + tw/2, y * th - top + th - floor_height - 0.1))
                    if "Goal" in properties and properties["Goal"] == "True":
                        self.goals.append(pygame.Rect((x * tw - left, y * th - top), (tw, th)))
                    if "Liftshaft" in properties and properties["Liftshaft"] == "True":
                        if (x, y) not in inshaft:
                            inshaft.append((x,y))
                            shaft_top = y
                            while shaft_top > 0:
                                prop = self.data.get_tile_properties(x, shaft_top-1, layer)
                                if "Liftshaft" not in prop or prop["Liftshaft"] != "True":
                                    break
                                shaft_top = shaft_top - 1
                                inshaft.append((x,shaft_top))
                            shaft_bottom = y
                            while shaft_bottom < self.data.height-1:
                                prop = self.data.get_tile_properties(x, shaft_bottom+1, layer)
                                if "Liftshaft" not in prop or prop["Liftshaft"] != "True":
                                    break
                                shaft_bottom = shaft_bottom + 1
                                inshaft.append((x,shaft_bottom))
                            self.shafts.append((x * tw - left + tw/2, shaft_top * th - top + th, shaft_bottom * th - top + th))
                    if "Button" in properties and properties["Button"] == "True":
                        if "Timeout" in properties:
                            timeout = float(properties["Timeout"])
                        else:
                            timeout = float("+inf")
                        if "Toggle" in properties:
                            toggle = properties["Toggle"] == "True"
                        else:
                            toggle = False
                        self.buttons.append(Button(pygame.Rect(x * tw - left, y * th - top, tw, th), self, properties["Target"], timeout, toggle))
                    if "Door" in properties and properties["Door"] == "True":
                        door = Door(pygame.image.load(os.path.join("data",properties["Openimg"])), pygame.Rect(x * tw - left, y * th - top, tw, th), wall, self.openDoors)
                        group = properties["Group"]
                        if group not in self.groups:
                            self.groups[group] = []
                        self.groups[group].append(door)
                    if "Spikes" in properties and properties["Spikes"] == "True":
                        floor_height = int(self.data.get_tileset_from_gid(self.data.get_tile_gid(x, y, layer)).properties["Floorheight"])
                        self.spikes.append(pygame.Rect((x * tw - left, y * th - top + th - floor_height*2), (tw, floor_height*2)))

    def draw(self, rect, surface):
        if self.data.background_color:
            surface.fill(pygame.Color(self.data.background_color))
        rect = rect.copy()
        surface.blit(self.surface, (0,0), area=rect)
        self.openDoors.draw(surface)
                    
class Button(object):
    def __init__(self, rect, level, target, timeout, toggle):
        self.pressed = False
        self.active = False
        self.rect = rect
        self.level = level
        self.target = target
        self.timeout = timeout
        self.toggle = toggle
        self.remaining = 0.0

    def press(self):
        self.pressed = True
        if self.toggle:
            self.set_active(not self.active)
        else:
            self.set_active(True)

    def release(self):
        self.pressed = False
        if self.active:
            self.remaining = self.timeout

    def update(self, dt):
        if self.active and not self.pressed:
            self.remaining -= dt
            if self.remaining <= 0.0:
                self.set_active(False)

    def set_active(self, active):
        if self.active != active:
            for door in self.level.groups[self.target]:
                door.set_open(active)
        self.active = active

class Door(pygame.sprite.Sprite):
    def __init__(self, img, rect, wall, openDoors):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = rect
        self.wall = wall
        self.openDoors = openDoors
        self.open = False

    def set_open(self, open):
        if open != self.open:
            if open:
                self.wall.solid = False
                self.openDoors.add(self)
            else:
                self.wall.solid = True
                self.openDoors.remove(self)
            self.open = open
