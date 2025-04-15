import numpy as np
from settings import N, K, DAMPING, RESORTING_FORCE, PROPAGATION_RANGE, PROPAGATION_WEIGHTS

class Wave:
    def __init__(self):
        self.y = np.zeros(N)
        self.velocity = np.zeros(N)

    def update(self):
        for i in range(PROPAGATION_RANGE, N - PROPAGATION_RANGE):
            sum_neighbors = 0
            for offset, weight in enumerate(PROPAGATION_WEIGHTS, start=1):
                sum_neighbors += weight * (self.y[i - offset] + self.y[i + offset])
            total_weight = 2 * sum(PROPAGATION_WEIGHTS)
            acceleration = K * ((sum_neighbors - total_weight * self.y[i]) / total_weight)
            self.velocity[i] += acceleration
            self.velocity[i] *= DAMPING
            self.velocity[i] -= RESORTING_FORCE * self.y[i]
        self.y += self.velocity

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