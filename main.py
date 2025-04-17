import pygame
import numpy as np
from settings import WIDTH, HEIGHT, N, MAX_FORCE_APPLIED, BOAT_SPEED, WAVE_BASE_HEIGHT, SIMULATION_STEPS
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

# debug
debug_mode = True

def apply_random_compression(wave):
    if np.random.rand() < 0.5:
        force = np.random.randint(200, 400)
    else:
        force = -np.random.randint(200, 400)
    wave.apply_compression_force(force, 50)

def reset_simulation():
    global wave, falling_objects
    wave = Wave()
    falling_objects = []
    boat.reset()

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
            elif event.key == pygame.K_F3:
                debug_mode = not debug_mode

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_q]:
        boat.move(-BOAT_SPEED)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        boat.move(BOAT_SPEED)

    # Compression aléatoire
    if compression_running:
        compression_timer += clock.get_time()
        if compression_timer >= compression_interval:
            apply_random_compression(wave)
            compression_timer = 0
            compression_interval = np.random.randint(500 / SIMULATION_STEPS, 2000 / SIMULATION_STEPS)

    # Gestion des objets qui tombent
    for obj in falling_objects[:]:
        obj.update()
        obj.draw(screen)
        wave_surface = WAVE_BASE_HEIGHT + wave.y[int(obj.x / WIDTH * N)]
        if obj.y + obj.radius >= wave_surface:
            if obj.interaction_count < MAX_FORCE_APPLIED:
                index = int(obj.x / WIDTH * N)
                # calcul de la force
                drop_height = max(0, wave_surface - obj.initial_y)
                normalized_drop_height = drop_height / (HEIGHT - obj.initial_y)
                force = 600 / np.pi * np.arctan(30 * (normalized_drop_height - 0.35)) + 282

                wave.apply_perturbation(index, force=force, spread=10)
                obj.interaction_count += 1
        if obj.is_out_of_bounds():
            falling_objects.remove(obj)

    # Mise à jour de la vague
    for _ in range(SIMULATION_STEPS):
        wave.update()
        wave.smooth(smoothing_factor=0.1) # base 0.5
        # Conditions de réflexion aux bords
        wave.y[0] = wave.y[1]
        wave.y[-1] = wave.y[-2]

    # Dessin de la vague
    points = [(x_positions[i], WAVE_BASE_HEIGHT + wave.y[i]) for i in range(N)]
    pygame.draw.aalines(screen, (100, 200, 255), False, points, 2)

    # Calcul et affichage du bateau
    # Trouver l'index de la vague sous le bateau selon sa position x
    boat_index = int((boat.x + boat.width // 2) / WIDTH * N)
    boat_index = max(1, min(N - 2, boat_index))  # éviter les bords

    wave_height = wave.y[boat_index]
    wave_surface_y = WAVE_BASE_HEIGHT + wave_height - boat.height // 2 + boat.y_offset
    slope = wave.y[boat_index + 1] - wave.y[boat_index - 1]
    angle = np.arctan(slope / (x_positions[1] - x_positions[0])) * boat.rotation_factor
    degrees = np.degrees(angle)
    boat.update(wave_height, clock, degrees, wave_surface_y)
    boat.draw(screen)

    # debug menu
    if debug_mode:
        font = pygame.font.SysFont("consolas", 20)
        debug_text = [
            f"FPS: {clock.get_fps():.2f}",
            f"Boat Y: {boat.y}",
            f"Boat X: {boat.x}",
            f"Boat Angle: {degrees:.2f}",
            f"Wave Height: {wave_height:.2f}",
            f"Wave Surface Y: {wave_surface_y:.2f}",
            f"Wave Index: {boat_index}",
            f"Wave Y: {wave.y[boat_index]:.2f}",
        ]
        for i, text in enumerate(debug_text):
            debug_surface = font.render(text, True, (255, 255, 255))
            screen.blit(debug_surface, (10, 10 + i * 25))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()