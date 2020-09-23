import sys 
import os.path as path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
rc('font', size=14, family='serif')
rc('text', usetex=True)

ωₙ = 1
ζ = np.linspace(0, 1, 512)
α = ζ * ωₙ
β = ωₙ * np.sqrt(1 - ζ**2)
ω = β

plt.figure(figsize=(8.5, 8.5*9/16))
plt.title(r'Damped frequency in function of the damping ratio $\zeta$')
plt.plot(ζ, ω / ωₙ)
plt.xlim([0, 1])
plt.ylim([0, 1])
plt.xlabel(r'$\zeta$')
plt.ylabel(r'$\omega_d / \omega_n$')
plt.tight_layout()
plt.savefig(path.join(path.dirname(sys.path[0]), 'images', 'damped-frequency.svg'))
plt.show()
