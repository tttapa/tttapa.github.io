import sys
import os.path as path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
rc('font', size=14, family='serif')
rc('text', usetex=True)

# Constants
m = 1
ζ = 1
ωₙ = 1

# Time constant
λ = -ζ * ωₙ

# Integration constants
c_3 = 1 / (m * ωₙ**2)
c_1 = -c_3
c_2 = c_3 * λ

# Time
t_end = 10
t = np.linspace(0, t_end, 512)

# Step response
x1 = c_1 * np.exp(λ * t) + c_3
x2 = c_2 * t * np.exp(λ * t)
x = x1 + x2

plt.figure(figsize=(8.5, 8.5 * 9 / 16))
plt.title('Step response of a critically damped harmonic oscillator')
plt.plot(t, x, label=r'$x(t) = c_1 e^{\lambda t} + c_2 t e^{\lambda t} + c_3$')
plt.plot(t, x1, '--', label=r'$c_1 e^{\lambda t} + c_3$')
plt.plot(t, x2, '--', label=r'$c_2 t e^{\lambda t}$')
plt.axhline(c_3, linestyle=':', color='k', linewidth=1)
plt.xlim([0, t_end])
plt.ylim([-0.5, 1.3])
plt.xlabel('$t$')
plt.ylabel('$x(t)$')
plt.legend()
plt.tight_layout()
plt.savefig(path.join(path.dirname(sys.path[0]), 'images', 'critically-damped.svg'))
plt.show()
