import pygame

import physics

class Platform(pygame.sprite.Sprite):
    """An wall or floor that is impassable to entities."""

    def __init__(self, image, (x, y), (vx, vy) = (0, 0), (ax, ay) = (0, 0)):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = image.get_rect()
        self.rect.topleft = (x, y)
        self.body = physics.Body((x, y), (self.rect.width, self.rect.height), (vx, vy), (ax, ay))

    def update(self, dt):
        self.body.update(dt)
        self.rect.topleft = self.body.pos
