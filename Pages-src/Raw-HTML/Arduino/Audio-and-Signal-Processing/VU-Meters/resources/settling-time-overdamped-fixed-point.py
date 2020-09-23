import sys 
import os.path as path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
from scipy.optimize import fixed_point
from scipy.stats import linregress
rc('font', size=14, family='serif')
rc('text', usetex=True)

# Constants
m = 1
ζ = np.linspace(1.0001, 3, 512*16)
ωₙ = 1

# Time constants
λ1 = -ωₙ*ζ + ωₙ*np.sqrt(ζ**2 - 1)
λ2 = -ωₙ*ζ - ωₙ*np.sqrt(ζ**2 - 1)

# Integration constants
c3 = 1 / (m * ωₙ**2)
c1 = c3 / (λ1/λ2 - 1)
c2 = c3 / (λ2/λ1 - 1)

# Approximation: c₁ exp(λ₁t) = 99% x(∞),
# as an initial guess for the iterative solver
t0_s = np.log(100 / (1 - λ1/λ2)) * (ζ + np.sqrt(ζ**2 - 1))

# Equation f(t) = t with same solution as x(t) = 99% x(∞)
f_s = lambda t: np.log((0.99 - 1 - np.exp(λ2*t)/(λ2/λ1 - 1)) * (λ1/λ2 - 1)) / λ1

# Solve x(t) = γ x(∞) numerically using fixed-point iterations
t_s = fixed_point(f_s, t0_s, xtol=1e-13)

# Linear regression of the rise time in function of the damping factor
slope, intercept, R, _, _ = linregress(ζ, t_s)
print(f'{slope=}, {intercept=}, R²={R**2}')

plt.figure(figsize=(8.5, 8.5*9/16))
plt.title(r'Settling time estimates in function of the damping ratio $\zeta$')
taylor_slope = 2*np.log(100)
plt.plot(ζ, t_s * ωₙ, label=r'True numerical solution: $t_s\omega_n$', linewidth=1)
plt.plot(ζ, t0_s * ωₙ, label=r'Estimate: $\tilde{t}_s\omega_n = \log \left(\frac{100}{1-\lambda_1/\lambda_2}\right) \left(\zeta + \sqrt{\zeta^2 - 1}\right)$', linewidth=1)
plt.plot(ζ, ζ * taylor_slope, label=r'Linear approximation: $\tilde{t}_s\omega_n \approx 2 \log \left(100\right)\zeta$', linewidth=1)
# plt.plot(ζ, ζ * slope + intercept, 'k', label='Linear regression of numerical result', linewidth=0.5)
plt.xlim([1, ζ[-1]])
plt.ylim([0, ζ[-1] * slope + intercept])
plt.xlabel(r'$\zeta$')
plt.ylabel(r'$t_s \cdot \omega_n$')
plt.legend()
plt.tight_layout()
plt.savefig(path.join(path.dirname(sys.path[0]), 'images', 'settling-time-overdamped.svg'))

plt.figure(figsize=(8.5, 8.5*9/16))
plt.title(r'Settling time estimates without asymptotes in function of the damping ratio $\zeta$')
taylor_slope = 2*np.log(100)
linear = ζ * taylor_slope
plt.plot(ζ, linear - t_s * ωₙ, label=r'True numerical solution: $2\log \left(100\right) \zeta - t_s\omega_n$', linewidth=1)
plt.plot(ζ, linear - t0_s * ωₙ, label=r'Estimate: $2\log \left(100\right) \zeta - \tilde{t}_s\omega_n$', linewidth=1)
plt.xlim([1, ζ[-1]])
plt.ylim([0, 2.75])
plt.xlabel(r'$\zeta$')
plt.ylabel(r'$2\log \left(100\right) \zeta - t_s \cdot \omega_n$')
plt.legend()
plt.tight_layout()
plt.savefig(path.join(path.dirname(sys.path[0]), 'images', 'settling-time-overdamped-error.svg'))

plt.show()
