import pygame
import numpy as np
from settings import WIDTH, HEIGHT, N, MAX_FORCE_APPLIED, BOAT_SPEED, WAVE_BASE_HEIGHT, SIMULATION_STEPS
from w4ve import Wave
from boat import Boat
from falling_object import FallingObject
from utils import draw_gradient_background
from particle import Splash
from animated_sprite import AnimatedSprite

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

# particule
splashes = []

# boat
prev_speed = boat.velocity_y

# variable qui change si on veux que la vague change de bord quand la vague touche le bord de l'écran
change_side = False

# oiseau animé
sheet = pygame.image.load("assets/pigeon_fiy-Sheet.png").convert_alpha()
# split the sheet into individual frames
frame_width = 32
frame_height = 32
frames = []
for i in range(6):
    frame = sheet.subsurface((i * frame_width, 0, frame_width, frame_height))
    frames.append(frame)

# Liste d'oiseaux animés
max_birds = 3
birds = []
for i in range(3):  # Exemple : 3 oiseaux
    birds.append(AnimatedSprite((600 + i*50, 50 + 50*i), frames))

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
            elif event.key == pygame.K_F4:
                change_side = not change_side
                reset_simulation()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] or keys[pygame.K_q]:
        boat.move(-BOAT_SPEED, change_side)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        boat.move(BOAT_SPEED, change_side)
    if keys[pygame.K_UP] or keys[pygame.K_z]:
        boat.jump()

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
        wave.update(change_side)
        wave.smooth(smoothing_factor=0.2) # base 0.5

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
    boat.draw(screen, change_side)

    # Gestion des éclaboussures
    if boat.landing:
        splash_x = boat.x + boat.width // 2
        splash_y = boat.y + boat.height // 2 - boat.y_offset
        if prev_speed < 0:
            continue
        splashes.append(Splash(splash_x, splash_y, num_particles=15, color=(100, 200, 255), speed_factor=abs(prev_speed / 10)))

    # Mise à jour et dessin des éclaboussures
    for splash in splashes[:]:
        splash.update(wave)
        splash.draw(screen)
        if splash.particles == []:
            splashes.remove(splash)

    # mise à jour de la vitesse precedente du bateau
    prev_speed = boat.velocity_y

    # debug menu
    if debug_mode:
        font = pygame.font.SysFont("consolas", 20)
        debug_text = [
            f"FPS: {clock.get_fps():.2f}",
            f"Boat Y: {boat.y}",
            f"Boat X: {boat.x}",
            f"Boat Velocity Y: {boat.velocity_y:.2f}",
            f"Boat Angle: {degrees:.2f}",
            f"Wave Height: {wave_height:.2f}",
            f"Wave Surface Y: {wave_surface_y:.2f}",
            f"Wave Index: {boat_index}",
            f"Wave Y: {wave.y[boat_index]:.2f}",
            f"Mode sans rebond" if change_side else "Mode rebond",
        ]
        for i, text in enumerate(debug_text):
            debug_surface = font.render(text, True, (255, 255, 255))
            screen.blit(debug_surface, (10, 10 + i * 25))

    # Affichage et mise à jour des oiseaux animés
    for bird in birds[:]:
        bird.update(clock.get_time())
        bird.draw(screen)
        # Suppression si mort et hors écran (exemple : y > HEIGHT)
        if bird.dead and bird.rect.y > HEIGHT:
            birds.remove(bird)
            # Ajout d'un nouvel oiseau à une position y aléatoire
            if len(birds) < max_birds:
                new_y = np.random.randint(50, 151)
                birds.append(AnimatedSprite((-32, new_y), frames))

    # Détection de la collision entre le bateau et les oiseaux
    boat_rect = pygame.Rect(boat.x, boat.y, boat.width, boat.height)
    for bird in birds:
        if boat_rect.colliderect(bird.rect) and boat.velocity_y > 0 and not bird.dead:
            boat.velocity_y = -5
            bird.death()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()