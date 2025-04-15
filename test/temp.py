import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm

seuil_max = 6  # Définir la valeur maximale à dépasser
iterations = 100  # Nombre maximum d'itérations

for i in tqdm(range(iterations)):
    t = np.linspace(0, 3456000000, 1000000)
    A = np.array(np.random.uniform(0.1, 0.2, size=100))
    omega = np.array(np.random.uniform(2 * np.pi / 12, 2 * np.pi / 18, size=100))
    phi = np.array(np.random.uniform(0, 2 * np.pi, size=100))

    waves = A[:, None] * np.sin(omega[:, None] * t + phi[:, None])
    ocean = np.einsum('ij->j', waves)

    max_value = np.max(ocean)
    max_index = np.argmax(ocean)

    if max_value > seuil_max:
        print(f"Iteration {i + 1}: Valeur maximale {max_value} dépasse le seuil {seuil_max}.")
        
        start_index = max(0, max_index - 150)
        end_index = min(len(ocean), max_index + 150)

        t_centered = t[start_index:end_index]
        ocean_centered = ocean[start_index:end_index]

        plt.figure(figsize=(10, 6))

        # Premier sous-graphe : courbe complète
        plt.subplot(2, 1, 1)
        plt.plot(t, ocean)
        plt.title("Courbe complète")
        plt.xlabel("Temps")
        plt.ylabel("Amplitude")

        # Deuxième sous-graphe : courbe centrée
        plt.subplot(2, 1, 2)
        plt.plot(t_centered, ocean_centered)
        plt.title("Courbe centrée autour du maximum")
        plt.xlabel("Temps")
        plt.ylabel("Amplitude")

        plt.tight_layout()
        plt.show()
        break
else:
    print("Aucune valeur maximale n'a dépassé le seuil après 100 itérations.")