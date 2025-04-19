import pygame
import numpy as np
from settings import WIDTH, HEIGHT, N, BOAT_IMAGE_PATH

class Boat:
    def __init__(self):
        self.image = pygame.image.load(BOAT_IMAGE_PATH)
        self.image = pygame.transform.smoothscale(self.image.convert_alpha(), (50, 50))
        self.width, self.height = self.image.get_size()
        self.x = WIDTH // 2 - self.width // 2
        self.y_offset = -20
        self.in_air = False
        self.velocity_y = 0
        self.jump_threshold = -30
        self.jump_force = -5
        self.gravity = 0.5
        self.display_angle = 0.0
        self.lerp_speed = 0.3
        self.jump_timer = 0
        self.rotation_factor = 0.5
        self.facing_right = True
        self.landing = False
        self.was_in_air = False

    def update(self, wave_y, clock, slope, wave_surface_y):
        # mise à jour su landing
        if self.landing:
            self.landing = False
        prev_in_air = self.in_air

        if not self.in_air:
            self.y = wave_surface_y
            if wave_y <= self.jump_threshold:
                self.in_air = True
                self.jump_timer = 0
                self.velocity_y = -2 * (self.jump_threshold - wave_y) / 20
        else:
            self.jump_timer += clock.get_time()
            if self.jump_timer >= 100:
                self.velocity_y += self.gravity
            self.y += self.velocity_y
            if self.y >= wave_surface_y:
                self.y = wave_surface_y
                self.velocity_y = 0
                self.in_air = False
                self.jump_timer = 0

        self.landing = prev_in_air and not self.in_air

        """if not self.in_air:
            self.display_angle = slope
        else:
            self.display_angle += (0 - self.display_angle) * self.lerp_speed"""

        # Angle interpolation pour décollage ET atterrissage progressif
        target_angle = slope if not self.in_air else 0
        self.display_angle += (target_angle - self.display_angle) * self.lerp_speed

    def move(self, dx):
        self.x += dx
        self.x = max(0, min(self.x, WIDTH - self.width))
        if dx < 0:
            self.facing_right = False
        elif dx > 0:
            self.facing_right = True

    def draw(self, screen):
        angle = -self.display_angle if self.facing_right else self.display_angle
        rotated_boat = pygame.transform.rotate(self.image, angle)
        if not self.facing_right:
            rotated_boat = pygame.transform.flip(rotated_boat, True, False)
        rect = rotated_boat.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(rotated_boat, rect.topleft)

    def reset(self):
        self.x = WIDTH // 2 - self.width // 2
        self.y_offset = -20
        self.in_air = False
        self.velocity_y = 0
        self.jump_timer = 0
        self.display_angle = 0.0
        self.facing_right = True

    def jump(self):
        if not self.in_air:
            self.in_air = True
            self.jump_timer = 0
            self.velocity_y = self.jump_force * 2
            self.landing = False
