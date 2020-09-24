import sys
import os.path as path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
rc('font', size=14, family='serif')
rc('text', usetex=True)

# Constants
m = 1
ωₙ = 1
ζ_max = 3
ζ = np.linspace(1.00001, ζ_max, 1024)

# Time constants
λ1 = -ζ * ωₙ + ωₙ * np.sqrt(ζ**2 - 1)
λ2 = -ζ * ωₙ - ωₙ * np.sqrt(ζ**2 - 1)

# Integration constants
c_3 = 1 / (m * ωₙ**2)
c_1 = c_3 / (λ1/λ2 - 1)
c_2 = c_3 / (λ2/λ1 - 1)

plt.figure(figsize=(8.5, 8.5*9/16))
plt.subplot(121)
plt.title('Time constants in function\n of the damping ratio $\\zeta$')
plt.plot(ζ, -1/λ1, label=r'$-\tau_1 = -1 / \lambda_1$')
plt.plot(ζ, -1/λ2, label=r'$-\tau_2 = -1 / \lambda_2$')
plt.xlim([1, ζ_max])
plt.ylim([0, 2 * ζ_max])
plt.xlabel(r'$\zeta$')
plt.ylabel(r'$-\tau_{1,2}$')
plt.legend()

plt.subplot(122)
plt.title('Integration constants in function\nof the damping ratio $\\zeta$')
plt.plot(ζ, c_1, label=r'$c_1$')
plt.plot(ζ, c_2, label=r'$c_2$')
plt.axhline(0, linestyle='-', color='k', linewidth=0.5)
plt.axhline(-c_3, linestyle=':', color='k', linewidth=1)
plt.xlim([1, ζ_max])
plt.ylim([-3, 2])
plt.xlabel(r'$\zeta$')
plt.ylabel(r'$c_{1,2}$')
plt.legend()
plt.tight_layout()
plt.savefig(path.join(path.dirname(sys.path[0]), 'images', 'lambdas-overdamped.svg'))

plt.show()
