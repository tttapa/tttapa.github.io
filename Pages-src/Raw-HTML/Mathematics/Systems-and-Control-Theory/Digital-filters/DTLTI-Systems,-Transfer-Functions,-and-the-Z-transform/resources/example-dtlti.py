from numpy import array, arange, cos, pi

class ExampleDTLTISystem:
    def __init__(self, initial_state: float = 0.0):
        self.state = initial_state

    def __call__(self, x_n: float) -> float:
        # y[n] = (x[n] + x[n-1]) / 2
        y_n = (x_n + self.state) / 2.0
        # x[n] will be x[n-1] on the next time step, 
        # so save it in the system's state
        self.state = x_n
        return y_n

n = arange(9)                # Create the time variable [0,1,2,…,7,8]
x = cos(pi * n) + 2          # Generate the input signal x[n]

T = ExampleDTLTISystem(1.0)  # Instantiate the system with x[-1] = 1
y = map(T, x)                # Apply the transformation y[n] = T(x[n])

import os.path as path
import sys
import matplotlib.pyplot as plt
from matplotlib import rc
rc('font', size=14, family='serif')
rc('text', usetex=True)

plt.figure(figsize=(6, 8 * 9 / 16))
plt.subplot(211)
plt.stem(n, x, basefmt='none', use_line_collection=True)
plt.title(r'Input $x[n]$')
plt.ylabel(r'$x[n]$')
plt.xlim([-1, 9])
plt.ylim([0, 4])
plt.subplot(212)
plt.stem(n, list(y), basefmt='none', use_line_collection=True)
plt.title(r'Output $y[n]$')
plt.ylabel(r'$y[n]$')
plt.xlabel(r'Time step $n$')
plt.xlim([-1, 9])
plt.ylim([0, 4])
plt.tight_layout()
plt.savefig(path.join(path.dirname(sys.path[0]), 'images', 'example-dtlti.svg'))
plt.show()
