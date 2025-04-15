import pygame
import numpy as np
from settings import WIDTH, HEIGHT, N, MAX_FORCE_APPLIED, BOAT_SPEED
from w4ve import Wave
from boat import Boat
from falling_object import FallingObject
from utils import draw_gradient_background

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Coordonnées x de la vague
x_positions = np.linspace(0, WIDTH, N)

wave = Wave()
boat = Boat()
falling_objects = []

compression_running = False
compression_timer = 0
compression_interval = np.random.randint(1000, 3000)

def apply_random_compression(wave):
    force = np.random.randint(-400, 200)
    spread = np.random.randint(5, 20)
    wave.apply_compression_force(force, spread)

def reset_simulation():
    global wave, falling_objects
    wave = Wave()
    falling_objects = []

running = True
while running:
    draw_gradient_background(screen, (13, 95, 166), (10, 10, 40))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            falling_objects.append(FallingObject(mx, my))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                reset_simulation()
            elif event.key == pygame.K_RETURN:
                compression_running = not compression_running

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        boat.move(-BOAT_SPEED)
    if keys[pygame.K_RIGHT]:
        boat.move(BOAT_SPEED)

    # Compression aléatoire
    if compression_running:
        compression_timer += clock.get_time()
        if compression_timer >= compression_interval:
            apply_random_compression(wave)
            compression_timer = 0
            compression_interval = np.random.randint(500, 2000)

    # Gestion des objets qui tombent
    for obj in falling_objects[:]:
        obj.update()
        obj.draw(screen)
        wave_surface = HEIGHT // 2 + wave.y[int(obj.x / WIDTH * N)]
        if obj.y + obj.radius >= wave_surface:
            if obj.interaction_count < MAX_FORCE_APPLIED:
                index = int(obj.x / WIDTH * N)
                force = -((HEIGHT - obj.initial_y) / HEIGHT) * 300
                wave.apply_perturbation(index, force=-force, spread=8)
                obj.interaction_count += 1
        if obj.is_out_of_bounds():
            falling_objects.remove(obj)

    # Mise à jour de la vague
    wave.update()
    wave.smooth(smoothing_factor=0.3)

    # Dessin de la vague
    points = [(x_positions[i], HEIGHT // 2 + wave.y[i]) for i in range(N)]
    pygame.draw.aalines(screen, (100, 200, 255), False, points, 2)

    # Conditions de réflexion aux bords
    wave.y[0] = wave.y[1]
    wave.y[-1] = wave.y[-2]

    # Calcul et affichage du bateau
    # Trouver l'index de la vague sous le bateau selon sa position x
    boat_index = int((boat.x + boat.width // 2) / WIDTH * N)
    boat_index = max(1, min(N - 2, boat_index))  # éviter les bords

    wave_height = wave.y[boat_index]
    wave_surface_y = HEIGHT // 2 + wave_height - boat.height // 2 + boat.y_offset
    slope = wave.y[boat_index + 1] - wave.y[boat_index - 1]
    angle = np.arctan(slope / (x_positions[1] - x_positions[0])) * boat.rotation_factor
    degrees = np.degrees(angle)
    boat.update(wave_height, clock, degrees, wave_surface_y)
    boat.draw(screen)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()