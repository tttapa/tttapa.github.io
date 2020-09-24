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

# Approximation: c₁ exp(λ₁t) = 10% x(∞),
# as an initial guess for the iterative solver
t0_10 = np.log(c3 * (0.1 - 1) / c1) / λ1
t0_90 = np.log(c3 * (0.9 - 1) / c1) / λ1

# Equation f(t) = t with same solution as x(t) = 10% x(∞) and x(t) = 90% x(∞)
f_10 = lambda t: np.log((0.1 - 1 - np.exp(λ2*t)/(λ2/λ1 - 1)) * (λ1/λ2 - 1)) / λ1
f_90 = lambda t: np.log((0.9 - 1 - np.exp(λ2*t)/(λ2/λ1 - 1)) * (λ1/λ2 - 1)) / λ1

# Solve x(t) = γ x(∞) numerically using fixed-point iterations
t_10 = fixed_point(f_10, t0_10, xtol=1e-13)
t_90 = fixed_point(f_90, t0_90, xtol=1e-13)

# Rise time is the difference between the time at which we reach 10% of the 
# final value and 90% of the final value
t_r = t_90 - t_10
t0_r = t0_90 - t0_10 # Estimate

# Linear regression of the rise time in function of the damping factor
slope, intercept, R, _, _ = linregress(ζ, t_r)
print(f'{slope=}, {intercept=}, R²={R**2}')

plt.figure(figsize=(8.5, 8.5*9/16))
plt.title(r'Rise time estimates in function of the damping ratio $\zeta$')
taylor_slope = 2*np.log(9)
plt.plot(ζ, t_r * ωₙ, label=r'True numerical solution: $t_r\omega_n$', linewidth=1)
plt.plot(ζ, t0_r * ωₙ, label=r'Estimate: $\tilde{t}_r\omega_n = \log \left(9\right) \left(\zeta + \sqrt{\zeta^2-1}\right)$', linewidth=1)
plt.plot(ζ, ζ * taylor_slope, label=r'Linear approximation: $\tilde{t}_r\omega_n \approx 2 \log \left(9\right)\zeta$', linewidth=1)
# plt.plot(ζ, ζ * slope + intercept, 'k', label='Linear regression of numerical result', linewidth=0.5)
plt.xlim([1, ζ[-1]])
plt.ylim([0, ζ[-1] * slope + intercept])
plt.xlabel(r'$\zeta$')
plt.ylabel(r'$t_r \cdot \omega_n$')
plt.legend()
plt.tight_layout()
plt.savefig(path.join(path.dirname(sys.path[0]), 'images', 'risetime-overdamped.svg'))

plt.figure(figsize=(8.5, 8.5*9/16))
plt.title(r'Rise time estimates without asymptotes in function of the damping ratio $\zeta$')
taylor_slope = 2*np.log(9)
linear = ζ * taylor_slope
plt.plot(ζ, linear - t_r * ωₙ, label=r'True numerical solution: $2\log \left(9\right) \zeta - t_r\omega_n$', linewidth=1)
plt.plot(ζ, linear - t0_r * ωₙ, label=r'Estimate: $2\log \left(9\right) \zeta - \tilde{t}_r\omega_n$', linewidth=1)
plt.xlim([1, ζ[-1]])
plt.ylim([0, 2.2])
plt.xlabel(r'$\zeta$')
plt.ylabel(r'$2\log \left(9\right) \zeta - t_r \cdot \omega_n$')
plt.legend()
plt.tight_layout()
plt.savefig(path.join(path.dirname(sys.path[0]), 'images', 'risetime-overdamped-error.svg'))

plt.show()
