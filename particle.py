import pygame
import random
import math

class SplashParticle:
    def __init__(self, x, y, angle, speed, color):
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = speed
        self.radius = random.randint(2, 4)
        self.color = color
        self.alpha = 255
        self.life = 60

    def update(self):
        self.x += self.speed * math.cos(math.radians(self.angle))
        self.y += self.speed * math.sin(math.radians(self.angle))
        self.alpha -= 255 / self.life
        self.radius *= 0.99
        self.speed *= 0.97
        # gravité
        self.y += 1
    
    def draw(self, surface):
        if self.alpha > 0:
            s = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, int(self.alpha)), (5, 5), int(self.radius))
            surface.blit(s, (self.x - 5, self.y - 5))

class Splash:
    def __init__(self, x, y, color, speed_factor, num_particles=15):
        self.particles = []
        for _ in range(num_particles):
            angle = random.uniform(230, 310)
            speed = random.uniform(2, 5) * speed_factor
            self.particles.append(SplashParticle(x, y, angle, speed, color))

    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.alpha > 0]

    def draw(self, surface):
        for p in self.particles:
            p.draw(surface)