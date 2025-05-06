import pygame
import numpy as np

# Initialisation
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# Paramètres de la vague
N = 500  # nombre de points
wave_y = np.zeros(N)
wave_velocity = np.zeros(N)
damping = 0.999
k = 0.4
spread = 0
max_force_applied = 3
resorting_force = 0.005
compression_timer = 0
compression_interval = np.random.randint(1000, 3000)
compression_running = False
rotation_factor = 0.5
display_angle = 0.0
lerp_speed = 0.1

# parametre propagation
propagation_range = 3
propagation_weights = np.array([0.5, 0.3, 0.2])

# Coordonnées x de la vague
x_positions = np.linspace(0, WIDTH, N)

# sprite pygame
boat_image = pygame.image.load("assets/boat.png").convert_alpha()
boat_image = pygame.transform.scale(boat_image, (50, 50))
boat_width, boat_height = boat_image.get_size()
y_offset = -20

# boat setup
boat_x = WIDTH // 2 - boat_width // 2
boat_velocity_y = 0
jump_threshold = -30
boat_in_air = False
jump_force = -5
gravity = 0.5

# slider pour contrôler 

class FallingObject:
    def __init__(self, x, y, radius=10, color=(255, 100, 0)):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.velocity_y = 0
        self.initial_y = y
        self.interaction_count = 0
    
    def update(self):
        self.velocity_y += gravity
        self.y += self.velocity_y
    
    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)
    
    def is_out_of_bounds(self):
        return self.y - self.radius > HEIGHT


falling_object = []

def draw_gradient_background(surface, color_top, color_bottom):
    """Dessine un dégradé vertical sur le fond."""
    for y in range(HEIGHT):
        # Interpolation linéaire entre les deux couleurs
        ratio = y / HEIGHT
        r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
        g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
        b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

def apply_wave_perturbation(index, force, spread=8):
    """Applique une perturbation à la vague à un index donné."""
    """if 0 <= index < N:
        wave_y[index] += force"""
    for i in range(-spread, spread + 1):
        idx = index + i
        if 0 <= idx < N:
            # La force diminue avec la distance à l'impact
            attenuation = np.exp(-abs(i) / (spread / 2))
            wave_y[idx] += force * attenuation

def apply_compression_force(force, spread=8):
    """Applique une force de compression sur le côté droit de la vague."""
    for i in range(1, spread + 1):
        index = N - i  # Indices proches du bord droit
        if index >= 0:
            # La force diminue avec la distance au bord
            wave_y[index] += force * (1 - (i / spread))

def apply_random_compression():
    if np.random.rand() < 0.5:
        force = np.random.uniform(-400, -200)
    else:
        force = np.random.uniform(200, 400)
    spread = np.random.randint(5, 20)
    apply_compression_force(force, spread)

def smooth_wave(wave, smoothing_factor=0.1):
    """Applique un lissage à la vague en utilisant une moyenne glissante."""
    smoothed_wave = wave.copy()
    for i in range(1, len(wave) - 1):
        smoothed_wave[i] = (
            wave[i] * (1 - smoothing_factor) +
            (wave[i - 1] + wave[i + 1]) * (smoothing_factor / 2)
        )
    return smoothed_wave

def reset_simulation():
    """Réinitialise les paramètres de la simulation."""
    global wave_y, wave_velocity, falling_object
    wave_y = np.zeros(N)
    wave_velocity = np.zeros(N)
    falling_object = []

running = True
while running:
    draw_gradient_background(screen, (13, 95, 166), (10, 10, 40))  # Bleu clair en haut, bleu foncé en bas

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            falling_object.append(FallingObject(mx, my))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                reset_simulation()
            elif event.key == pygame.K_RETURN:
                compression_running = not compression_running

    # gestiion de la compressioin aleatoire
    if compression_running:
        compression_timer += clock.get_time()
        if compression_timer >= compression_interval:
            apply_random_compression()
            compression_timer = 0
            compression_interval = np.random.randint(500, 2000)

    # gestion des objets
    for obj in falling_object:
        obj.update()
        obj.draw(screen)

        # surface de la vague
        wave_surface = HEIGHT // 2 + wave_y[int(obj.x / WIDTH * N)]
        # Vérification de la collision avec la vague
        if obj.y + obj.radius >= wave_surface:
            if obj.interaction_count < max_force_applied:
                index = int(obj.x / WIDTH * N)
                force = -((HEIGHT - obj.initial_y) / HEIGHT) * 200
                apply_wave_perturbation(index, force=-force, spread=8)
                obj.interaction_count += 1

        if obj.is_out_of_bounds():
            falling_object.remove(obj)

    # Calcul des nouvelles positions (simulation physique)
    """for i in range(1, N - 1):
        acceleration = k * (wave_y[i - 1] + wave_y[i + 1] - 2 * wave_y[i])
        wave_velocity[i] += acceleration
        wave_velocity[i] *= damping
        wave_velocity[i] -= resorting_force * wave_y[i] """
    for i in range(propagation_range, N - propagation_range):
        sum_neighbors = 0
        for offset, weight in enumerate(propagation_weights, start=1):
            sum_neighbors += weight * (wave_y[i - offset] + wave_y[i + offset])
        total_weight = 2 * np.sum(propagation_weights)
        acceleration = k * ((sum_neighbors - total_weight * wave_y[i]) / total_weight)
        wave_velocity[i] += acceleration
        wave_velocity[i] *= damping
        wave_velocity[i] -= resorting_force * wave_y[i]

    wave_y += wave_velocity

    wave_y = smooth_wave(wave_y, smoothing_factor=0.3)  # Appliquer le lissage

    # Dessin de la ligne de vague
    points = [(x_positions[i], HEIGHT // 2 + wave_y[i]) for i in range(N)]
    pygame.draw.aalines(screen, (100, 200, 255), False, points, 2)

    # Appliquer conditions de réflexion aux bords
    wave_y[0] = wave_y[1]
    wave_y[-1] = wave_y[-2]

    # calculer la position du bateau
    wave_height = wave_y[N // 2]
    wave_surface_y = HEIGHT // 2 + wave_height - boat_height // 2 + y_offset
    
    # calculer l'angle de rotatioin en fonction de la pente locale
    slope = wave_y[N // 2 + 1] - wave_y[N // 2 - 1]
    angle = np.arctan(slope / (x_positions[1] - x_positions[0])) * rotation_factor
    degrees = np.degrees(angle)

    if not boat_in_air:
        boat_y = wave_surface_y

        if wave_height <= jump_threshold:
            boat_in_air = True
            jump_timer = 0
            boat_velocity_y = -2 * (jump_threshold - wave_height) / 20
    else:
        jump_timer += clock.get_time()
        
        if jump_timer >= 100:
            boat_velocity_y += gravity
        boat_y += boat_velocity_y

        if boat_y >= wave_surface_y:
            boat_y = wave_surface_y
            boat_velocity_y = 0
            boat_in_air = False
            jump_timer = 0

    if not boat_in_air:
        display_angle = degrees
    else:
        display_angle += (0 - display_angle) * lerp_speed

    rotated_boat = pygame.transform.rotate(boat_image, -display_angle)
    rotated_boat = pygame.transform.smoothscale(rotated_boat, rotated_boat.get_size())

    rotated_boat_rect = rotated_boat.get_rect(center=(boat_x + boat_width // 2, boat_y + boat_height // 2))

    screen.blit(rotated_boat, rotated_boat_rect.topleft)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
