import sys
import os.path as path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
rc('font', size=14, family='serif')
rc('text', usetex=True)

# Constants
m = 1
ζ = 1.15
ωₙ = 1

# Time constants
λ1 = -ζ * ωₙ + np.sqrt(ζ**2 - 1)
λ2 = -ζ * ωₙ - np.sqrt(ζ**2 - 1)

# Integration constants
c_3 = 1 / (m * ωₙ**2)
c_1 = c_3 / (λ1/λ2 - 1)
c_2 = c_3 / (λ2/λ1 - 1)

# Time
t_end = 10
t = np.linspace(0, t_end, 512)

# Step response
x1 = c_1 * np.exp(λ1 * t) + c_3
x2 = c_2 * np.exp(λ2 * t)
x = x1 + x2

plt.figure(figsize=(8.5, 8.5 * 9 / 16))
plt.title('Step response of an overdamped harmonic oscillator')
plt.plot(t, x, label=r'$x(t) = c_1 e^{\lambda_1 t} + c_2 e^{\lambda_2 t} + c_3$')
plt.plot(t, x1, '--', label=r'$c_1 e^{\lambda_1 t} + c_3$')
plt.plot(t, x2, '--', label=r'$c_2 e^{\lambda_2 t}$')
plt.axhline(c_3, linestyle=':', color='k', linewidth=1)
plt.xlim([0, t_end])
plt.ylim([-0.5, 1.3])
plt.xlabel('$t$')
plt.ylabel('$x(t)$')
plt.legend()
plt.tight_layout()
plt.savefig(path.join(path.dirname(sys.path[0]), 'images', 'overdamped.svg'))
plt.show()
