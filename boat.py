import pygame
import numpy as np
from settings import WIDTH, HEIGHT, N, BOAT_IMAGE_PATH
import time

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
        self.dash = False
        self.dash_cooldown = 0.5
        self.last_dash_time = 0
        self.max_height = 0
        self.prev_max_height = 0

    def update(self, wave_y, clock, slope, wave_surface_y, wave=None):
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
                self.max_height = self.y
        else:
            self.jump_timer += clock.get_time()
            if self.jump_timer >= 100:
                self.velocity_y += self.gravity
            self.y += self.velocity_y
            # mise à jour de la hauteur maximale
            if self.max_height == 0 or self.y < self.max_height:
                self.max_height = self.y
            if self.y >= wave_surface_y:
                self.y = wave_surface_y
                self.velocity_y = 0
                self.in_air = False
                self.jump_timer = 0

                # mise à jour de la hauteur maximale
                self.max_height = 0

        self.landing = prev_in_air and not self.in_air

        """if not self.in_air:
            self.display_angle = slope
        else:
            self.display_angle += (0 - self.display_angle) * self.lerp_speed"""

        # Angle interpolation pour décollage ET atterrissage progressif
        target_angle = slope if not self.in_air else 0
        self.display_angle += (target_angle - self.display_angle) * self.lerp_speed

        # Verifier le dash
        if self.dash:
            # verifier si le bateau touche la vague
            if self.y >= wave_surface_y:
                self.dash= False
                force = abs(self.prev_max_height - wave_surface_y) * 1.5
                wave.apply_perturbation(int((self.x + self.width // 2) / WIDTH * N), force=force, spread=15)

        self.prev_max_height = self.max_height

    def move(self, dx, change_side):
        self.x += dx
        if change_side:
            self.x = self.x % WIDTH
        else:
            self.x = max(0, min(self.x, WIDTH - self.width))

        if dx < 0:
            self.facing_right = False
        elif dx > 0:
            self.facing_right = True

    def draw(self, screen, change_side):
        angle = -self.display_angle if self.facing_right else self.display_angle
        rotated_boat = pygame.transform.rotate(self.image, angle)
        if not self.facing_right:
            rotated_boat = pygame.transform.flip(rotated_boat, True, False)
        rect = rotated_boat.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        screen.blit(rotated_boat, rect.topleft)

        if change_side:
            # Dessin du bateau à gauche et à droite de l'écran
            if self.x < self.width:
                rect_right = rotated_boat.get_rect(center=(self.x + WIDTH + self.width // 2, self.y + self.height // 2))
                screen.blit(rotated_boat, rect_right.topleft)
            # Si le bateau est proche du bord droit, dessine-le aussi à gauche
            if self.x > WIDTH - self.width:
                rect_left = rotated_boat.get_rect(center=(self.x - WIDTH + self.width // 2, self.y + self.height // 2))
                screen.blit(rotated_boat, rect_left.topleft)

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
    
    def smash_dash(self, waves):
        now = time.time()
        if self.in_air and not self.dash and (now - self.last_dash_time) >= self.dash_cooldown:
            self.dash = True
            self.velocity_y = -self.jump_force * 6
            self.last_dash_time = now
