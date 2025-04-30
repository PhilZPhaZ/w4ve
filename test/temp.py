import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import scipy.signal
from tqdm import tqdm
from numba import njit
import concurrent.futures
import scipy

seuil_max = 0
iterations = 10000

best_max_value = -np.inf
best_ocean = None
best_t = None
best_max_index = None

@njit
def compute_ocean(A, omega, phi, t):
    waves = A[:, None] * np.sin(omega[:, None] * t + phi[:, None])
    return np.sum(waves, axis=0)

_ = compute_ocean(
    np.ones(10, dtype=np.float32),
    np.ones(10, dtype=np.float32),
    np.ones(10, dtype=np.float32),
    np.ones(100, dtype=np.float32)
)

plt.ioff()

def simulate_once(_):
    t = np.linspace(0, 345600, 10000, dtype=np.float32)
    A = np.random.uniform(0.1, 0.2, size=200).astype(np.float32) # 0.1, 0.2
    omega = np.random.uniform(2 * np.pi / 12, 2 * np.pi / 18, size=200).astype(np.float32)
    phi = np.random.uniform(0, 2 * np.pi, size=200).astype(np.float32)
    ocean = compute_ocean(A, omega, phi, t)
    max_value = np.max(ocean)
    max_index = np.argmax(ocean)
    return max_value, ocean, t, max_index, A, omega, phi

if __name__ == "__main__":
    results = []
    with concurrent.futures.ProcessPoolExecutor(max_workers=50) as executor:
        for result in tqdm(executor.map(simulate_once, range(iterations)), total=iterations):
            results.append(result)

    best_max_value = -np.inf
    best_ocean = None
    best_t = None
    best_max_index = None
    best_A = None
    best_omega = None
    best_phi = None

    for max_value, ocean, t, max_index, A, omega, phi in results:
        if max_value > best_max_value:
            best_max_value = max_value
            best_ocean = ocean
            best_t = t
            best_max_index = max_index
            best_A = A
            best_omega = omega
            best_phi = phi

    # Après la boucle, afficher seulement la meilleure courbe
    if best_ocean is not None:
        start_index = max(0, best_max_index - 150)
        end_index = min(len(best_ocean), best_max_index + 150)

        t_centered = best_t[start_index:end_index]
        ocean_centered = best_ocean[start_index:end_index]

        sigma = np.std(best_ocean)

        plt.figure(figsize=(15, 6))

        gs = gridspec.GridSpec(2, 2, width_ratios=[2, 2])
        # Courbe complète (en haut à gauche)
        ax1 = plt.subplot(gs[0, 0])
        ax1.plot(best_t, best_ocean)
        ax1.scatter(best_t[best_max_index], best_max_value, color='red', label='Max')
        ax1.annotate(f'Max: {best_max_value:.2f}', (best_t[best_max_index], best_max_value),
                    xytext=(10, -10), textcoords='offset points', color='red')
        ax1.set_title("Courbe complète")
        ax1.set_xlabel("Temps")
        ax1.set_ylabel("Amplitude")
        ax1.legend()

        # Courbe centrée (en bas à gauche)
        ax2 = plt.subplot(gs[1, 0])
        ax2.plot(t_centered, ocean_centered)
        ax2.scatter(best_t[best_max_index], best_max_value, color='red', label='Max')
        ax2.annotate(f'Max: {best_max_value:.2f}', (best_t[best_max_index], best_max_value),
                    xytext=(10, -10), textcoords='offset points', color='red')
        ax2.set_title("Courbe centrée autour du maximum")
        ax2.set_xlabel("Temps")
        ax2.set_ylabel("Amplitude")
        ax2.legend()

        # Histogramme à droite (prend les deux lignes)
        peaks, _ = scipy.signal.find_peaks(best_ocean, height=0)
        amplitudes = best_ocean[peaks]
        ax3 = plt.subplot(gs[:, 1])
        ax3.hist(amplitudes, bins=30, color='blue', alpha=0.7, edgecolor='black', density=True)
        ax3.set_title("Histogramme des amplitudes des pics")
        ax3.set_xlabel("Amplitude")
        ax3.set_ylabel("Fréquence")

        # calcul de la proba vague scelerate
        seuil = 5 * sigma
        proba = np.sum(amplitudes > seuil) / len(amplitudes)

        # Affichage en bas de la figure
        plt.figtext(0.5, 0.01, f"Sigma: {sigma:.2f}    |    Proba > {seuil:.2f}: {proba:.10%}", 
                    ha='center', fontsize=12, color='black')

        plt.tight_layout()
        plt.show()