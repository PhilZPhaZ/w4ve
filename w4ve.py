import numpy as np
from settings import N, K, DAMPING, RESORTING_FORCE, PROPAGATION_RANGE, PROPAGATION_WEIGHTS, ALPHA, HEIGHT, WAVE_BASE_HEIGHT

class Wave:
    def __init__(self):
        self.y = np.zeros(N)
        self.velocity = np.zeros(N)

    def update(self, change_side=False):
        #for i in range(PROPAGATION_RANGE, N - PROPAGATION_RANGE):
        if change_side:
            indices = range(N)
        else:
            indices = range(PROPAGATION_RANGE, N - PROPAGATION_RANGE)
        self._update_indices(indices)
        self._add_noise()

    def _update_indices(self, indices):
        for i in indices:
            sum_neighbors = 0
            for offset, weight in enumerate(PROPAGATION_WEIGHTS, start=1):
                left = (i - offset) % N
                right = (i + offset) % N
                # sum_neighbors += weight * (self.y[i - offset] + self.y[i + offset])
                sum_neighbors += weight * (self.y[left] + self.y[right])
            total_weight = 2 * sum(PROPAGATION_WEIGHTS)
            # facteur de non-linéarité
            non_linear = 1 + ALPHA * (self.y[i] / (HEIGHT - WAVE_BASE_HEIGHT))
            acceleration = K * ((sum_neighbors - total_weight * self.y[i]) / total_weight)
            self.velocity[i] += acceleration
            self.velocity[i] *= DAMPING
            self.velocity[i] -= RESORTING_FORCE * self.y[i]
        self.y += self.velocity

    def _add_noise(self, std=0.05):
        self.y += np.random.normal(0, std, size=N)  # Ajout de bruit aléatoire

    def smooth(self, smoothing_factor=0.3):
        smoothed = self.y.copy()
        for i in range(1, len(self.y) - 1):
            smoothed[i] = (
                self.y[i] * (1 - smoothing_factor) +
                (self.y[i - 1] + self.y[i + 1]) * (smoothing_factor / 2)
            )
        self.y = smoothed

    def apply_perturbation(self, index, force, spread=8):
        for i in range(-spread, spread + 1):
            idx = index + i
            if 0 <= idx < N:
                attenuation = np.exp(-abs(i) / (spread / 2))
                self.y[idx] += force * attenuation
    
    def apply_compression_force(self, force, spread=8):
        for i in range(1, spread + 1):
            index = len(self.y) - i  # Indices proches du bord droit
            if index >= 0:
                attenuation = 1 - (i / (spread + 1))
                self.y[index] += force * attenuation