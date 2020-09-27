from numpy import array, arange
import os.path as path
import sys
import matplotlib.pyplot as plt
from matplotlib import rc
rc('font', size=14, family='serif')
rc('text', usetex=True)

n = arange(-4, 5)
d = n == 0
U = n >= 0

plt.figure(figsize=(6, 5.5 * 9 / 16))
plt.axhline(0, linestyle='-', linewidth=0.5, color='k')
plt.stem(n, d, basefmt='none', use_line_collection=True)
plt.title(r'Kronecker Delta Function $\delta[n]$')
plt.ylabel(r'$\delta[n]$')
plt.xlabel(r'Time step $n$')
plt.xlim([-4.5, 4.5])
plt.tight_layout()
plt.savefig(path.join(path.dirname(sys.path[0]), 'images', 'kronecker.svg'))

plt.figure(figsize=(6, 5.5 * 9 / 16))
plt.axhline(0, linestyle='-', linewidth=0.5, color='k')
plt.stem(n, U, basefmt='none', use_line_collection=True)
plt.title(r'Heaviside Step Function $u[n]$')
plt.ylabel(r'$u[n]$')
plt.xlabel(r'Time step $n$')
plt.xlim([-4.5, 4.5])
plt.tight_layout()
plt.savefig(path.join(path.dirname(sys.path[0]), 'images', 'heaviside.svg'))

plt.show()
