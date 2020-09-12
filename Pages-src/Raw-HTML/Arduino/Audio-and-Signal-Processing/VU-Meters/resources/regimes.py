import sys 
import os.path as path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
rc('font', size=14, family='serif')
rc('text', usetex=True)

def step_response_x(m, ζ, ωₙ, t_end=10):
    ζ
    t = np.linspace(0, t_end, 512)

    discriminant = ζ**2 - 1
    if abs(discriminant) > 1e-10: # Two distinct roots (real or complex)
        lambda_1 = -ζ * ωₙ + ωₙ * np.sqrt(discriminant + 0j)
        lambda_2 = -ζ * ωₙ - ωₙ * np.sqrt(discriminant + 0j)

        c_3 = 1 / (m * ωₙ**2)
        c_1 = c_3 / (lambda_1 / lambda_2 - 1)
        c_2 = c_3 / (lambda_2 / lambda_1 - 1)

        x = c_1 * np.exp(lambda_1 * t) + c_2 * np.exp(lambda_2 * t) + c_3
    else: # One root with multiplicity 2 (real)
        lambda_ = -ζ * ωₙ

        c_3 = 1 / (m * ωₙ**2)
        c_1 = -c_3
        c_2 = -c_1 * lambda_

        x = c_1 * np.exp(lambda_ * t) + c_2 * t * np.exp(lambda_ * t) + c_3
    return t, np.real_if_close(x)

m = 1
ωₙ = 1
t_end = 12

plt.figure(figsize=(8.5, 8.5*9/16))
plt.title('Step response of the damped harmonic oscillator in different regimes')
plt.plot(*step_response_x(m, 0.4, ωₙ, t_end), label='Underdamped')
plt.plot(*step_response_x(m, 1.0, ωₙ, t_end), label='Critically damped')
plt.plot(*step_response_x(m, 2.0, ωₙ, t_end), label='Overdamped')
plt.axhline(1, linestyle=':', color='k', linewidth=1)
plt.xlim([0, t_end])
plt.ylim([0, 1.3])
plt.xlabel('$t$')
plt.ylabel('$x(t)$')
plt.legend()
plt.tight_layout()
plt.savefig(path.join(path.dirname(sys.path[0]), 'images', 'regimes.svg'))
plt.show()
