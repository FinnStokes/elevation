import pygame
from pygame.locals import *
import pytmx
import util_pygame as pytmxutil

class Level():
    """A tile-based level"""

    def __init__(self, filename):
        self.data = pytmxutil.load_pygame(filename)
        self.surface = pygame.Surface((self.data.width*self.data.tilewidth, self.data.width*self.data.tilewidth))
        self.refresh(self.surface.get_rect())
        i = self.data.visible_tile_layers.next()
        self.passable = [[self.data.get_tile_properties(x, y, i)['Passable'] == "True" for y in xrange(self.data.height)] for x in xrange(self.data.width)]
        self.transparent = [[self.data.get_tile_properties(x, y, i)['Transparent'] == "True" for y in xrange(self.data.height)] for x in xrange(self.data.width)]

    def refresh(self, rect):
        surface_blit = self.surface.blit
        tw = self.data.tilewidth
        th = self.data.tileheight
        top = rect.top
        left = rect.left

        if self.data.background_color:
            surface.fill(pygame.Color(self.data.background_color))

        for layer in self.data.visible_layers:
            # draw map tile layers
            if isinstance(layer, pytmx.TiledTileLayer):
                # iterate over the tiles in the layer
                for x, y, image in layer.tiles():
                    surface_blit(image, (x * tw - left, y * th - top))

    def draw(self, rect, surface):
        if self.data.background_color:
            surface.fill(pygame.Color(self.data.background_color))
        rect = rect.copy()
        rect.left += self.dx
        rect.top += self.dy
        surface.blit(self.surface, (0,0), area=rect)
                    