# ...existing code...
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Paramètres
n = 200
x = np.linspace(0, 10, n)
y = np.zeros(n)
v = np.zeros(n)
c = 1.0
dx = x[1] - x[0]
dt = 0.01

def update_wave(frame):
    global y, v
    a = c**2 * (np.roll(y,1) - 2*y + np.roll(y,-1)) / dx**2
    v += a*dt
    y += v*dt
    line.set_ydata(y)
    return line,

def on_click(event):
    if event.xdata is not None:
        idx = int(event.xdata/dx) % n
        y[idx] += 1.0  # Perturbation

fig, ax = plt.subplots()
line, = ax.plot(x, y)
ax.set_ylim(-2, 2)
cid = fig.canvas.mpl_connect('button_press_event', on_click)
ani = FuncAnimation(fig, update_wave, interval=30, blit=True)
plt.show()