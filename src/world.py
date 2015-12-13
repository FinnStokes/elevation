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
        self.walls = []
        self.goal = None
        self.spawn = (0,0)
        self.refresh(self.surface.get_rect())

    def refresh(self, rect):
        surface_blit = self.surface.blit
        tw = self.data.tilewidth
        th = self.data.tileheight
        top = rect.top
        left = rect.left

        if self.data.background_color:
            self.surface.fill(pygame.Color(self.data.background_color))

        for layer in self.data.visible_tile_layers:
            # iterate over the tiles in the layer
            for x, y, image in self.data.layers[layer].tiles():
                surface_blit(image, (x * tw - left, y * th - top))
                properties = self.data.get_tile_properties(x, y, layer)
                if properties:
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
                        self.walls.append(physics.Body((fx, fy), (wall_width, th)))
                    if "Spawn" in properties and properties["Spawn"] == "True":
                        floor_height = int(self.data.get_tileset_from_gid(self.data.get_tile_gid(x, y, layer)).properties["Floorheight"])
                        self.spawn = (x * tw - left + tw/2, y * th - top + th - floor_height - 0.1)
                    if "Goal" in properties and properties["Goal"] == "True":
                        self.goal = pygame.Rect((x, y), (tw, th))

    def draw(self, rect, surface):
        if self.data.background_color:
            surface.fill(pygame.Color(self.data.background_color))
        rect = rect.copy()
        surface.blit(self.surface, (0,0), area=rect)
                    
