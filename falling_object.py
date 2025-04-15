import pygame
from settings import HEIGHT

class FallingObject:
    def __init__(self, x, y, radius=10, color=(255, 100, 0)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.velocity_y = 0
        self.initial_y = y
        self.interaction_count = 0
        self.gravity = 0.5

    def update(self):
        self.velocity_y += self.gravity
        self.y += self.velocity_y

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    def is_out_of_bounds(self):
        return self.y - self.radius > HEIGHT