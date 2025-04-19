import pygame
from settings import WIDTH, HEIGHT

def draw_gradient_background(surface, color_top, color_bottom):
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
