import sys
import os.path as path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
from scipy.optimize import fixed_point
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

# Equation for settling time: f(t) = t
γ_s = 0.99
f_s = lambda t: np.log((γ_s - 1) / (λ * t - 1)) / λ

t_s = float(fixed_point(f_s, 1 / ωₙ, xtol=1e-14))
print(f'{t_s=}')
print(f'{t_s*ωₙ=}')

# Equation for rise time: f(t) = t
γ_1 = 0.10
f_1 = lambda t: np.log((γ_1 - 1) / (λ * t - 1)) / λ
γ_2 = 0.90
f_2 = lambda t: np.log((γ_2 - 1) / (λ * t - 1)) / λ

t_1 = float(fixed_point(f_1, 1 / ωₙ, xtol=1e-14))
t_2 = float(fixed_point(f_2, 1 / ωₙ, xtol=1e-14))
t_r = t_2 - t_1
print(f'{t_r=}')
print(f'{t_r*ωₙ=}')

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
plt.axhline(γ_s * c_3, linestyle=':', color='k', linewidth=1)
plt.axhline(γ_1 * c_3, linestyle=':', color='k', linewidth=1)
plt.axhline(γ_2 * c_3, linestyle=':', color='k', linewidth=1)
plt.axvline(t_1, linestyle=':', color='k', linewidth=1)
plt.axvline(t_2, linestyle=':', color='k', linewidth=1)
plt.axvline(t_s, linestyle=':', color='k', linewidth=1)
plt.axhline(c_3, linestyle=':', color='k', linewidth=1)
plt.xlim([0, t_end])
plt.ylim([-0.5, 1.3])
plt.xlabel('$t$')
plt.ylabel('$x(t)$')
plt.legend()
plt.tight_layout()
name = 'critically-damped-rise-settling-time.svg'
plt.savefig(path.join(path.dirname(sys.path[0]), 'images', name))
plt.show()
