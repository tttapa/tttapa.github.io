import sys 
import os.path as path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
rc('font', size=14, family='serif')
rc('text', usetex=True)

ζ = np.linspace(0, 0.99999, 512)
po = 100 * np.exp(-np.pi * ζ / np.sqrt(1 - ζ**2))

plt.figure(figsize=(8.5, 8.5*9/16))
plt.title(r'Percent overshoot in function of the damping ration $\zeta$')
plt.plot(ζ, po)
plt.xlim([0, 1])
plt.ylim([0, 100])
plt.xlabel(r'$\zeta$')
plt.ylabel('P.O.')
plt.tight_layout()
plt.savefig(path.join(path.dirname(sys.path[0]), 'images', 'overshoot.svg'))
plt.show()
