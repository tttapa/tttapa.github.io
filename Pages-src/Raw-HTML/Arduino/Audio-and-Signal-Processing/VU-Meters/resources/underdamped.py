import sys
import os.path as path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
rc('font', size=14, family='serif')
rc('text', usetex=True)

# Constants
π = np.pi
m = 1
ζ = 0.1
ωₙ = 1

# Derived constants
α = ζ * ωₙ
β = ωₙ * np.sqrt(1 - ζ**2)

# Rise time and overshoot
t_r = 1 / β * (np.pi - np.arctan2(β, α))
t_s = - np.log(0.01) / α
po = 100 * np.exp(-α * π / β)

print(f'{t_r=}')
print(f'{t_s=}')
print(f'{po=}')

# Integration constants
c_3 = 1 / (m * ωₙ**2)
ct_1 = -c_3
ct_2 = -c_3 * α / β

# Time
t_end = 50
t = np.linspace(0, t_end, 512)

# Step response
response = lambda t: \
    np.exp(-α * t) * (ct_1 * np.cos(β * t) + ct_2 * np.sin(β * t)) + c_3
x = response(t)

# Local extrema of the step response
t_extrema = π / β * np.arange(1, np.floor(β * t_end / π) + 1)
x_extrema = response(t_extrema)

# Exponential “bounds” on the extrema
upperbound = +ct_1 * np.exp(-α * t) + c_3
lowerbound = -ct_1 * np.exp(-α * t) + c_3

plt.figure(figsize=(8.5, 8.5 * 9 / 16))
plt.title('Step response of an underdamped harmonic oscillator')
plt.plot(t, x, label='$x(t)$')
# plt.plot(t, upperbound, 'k:', linewidth=1, label=r'$x(\infty) \left(1 \pm \exp(-\alpha t)\right)$')
plt.plot(t, upperbound, 'k:', linewidth=1, label=r'$x(\infty) \Big(1 \pm e^{-\alpha t}\Big)$')
plt.plot(t, lowerbound, 'k:', linewidth=1)
plt.plot(t_extrema, x_extrema, 'r.', linewidth=1, label='Local extrema')
# plt.axhline(c_3, linestyle=':', color='k', linewidth=1)
# plt.axvline(t_r, linestyle='-', color='r', linewidth=1)
plt.xlim([0, t_end])
plt.ylim([0, 2 * c_3])
plt.xlabel('$t$')
plt.ylabel('$x(t)$')
plt.legend()
plt.tight_layout()
plt.savefig(path.join(path.dirname(sys.path[0]), 'images', 'underdamped.svg'))
plt.show()
