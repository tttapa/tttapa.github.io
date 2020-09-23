import sys 
import os.path as path
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rc
from scipy.optimize import fixed_point, minimize
rc('font', size=14, family='serif')
rc('text', usetex=True)

# Constants
m = 1
ζ = np.linspace(1.000001, 10, 512*16)
ωₙ = 1

# Time constants
λ1 = -ωₙ*ζ + ωₙ*np.sqrt(ζ**2 - 1)
λ2 = -ωₙ*ζ - ωₙ*np.sqrt(ζ**2 - 1)

# Integration constants
c3 = 1 / (m * ωₙ**2)
c1 = c3 / (λ1/λ2 - 1)
c2 = c3 / (λ2/λ1 - 1)

# Step response and its derivatives
x = lambda t: c1 * np.exp(λ1 * t) + c2 * np.exp(λ2 * t) + c3
x_dot = lambda t: c1 * λ1 * np.exp(λ1 * t) + c2 * λ2 * np.exp(λ2 * t)
x_dot2 = lambda t: c1 * λ1**2 * np.exp(λ1 * t) + c2 * λ2**2 * np.exp(λ2 * t)

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

# Slope of the asymptote for ζ → ∞
slope = 2*np.log(9)

def get_approx(x):
    δ, c, p = tuple(x)
    ζ_test = 1e8
    h = 0.5 * slope * (ζ_test + np.sqrt(ζ_test**2 - 1)) \
      - 0.5 * slope * (ζ_test + np.power(np.power(ζ_test + δ, p) - c, 1/p))
    return 0.5 * slope * (ζ + np.power(np.power(ζ + δ, p) - c, 1/p)) + h

def cost(param):
    approx = get_approx(param)
    diff = approx - t_r        # Compare approximation to the numerical result
    return np.dot(diff, diff)  # Norm squared of the difference

param0 = np.array([0, 1, 2])

res = minimize(cost, param0, method='Nelder-Mead')
print (res)
sol = res.x
approx = get_approx(sol)

plt.figure(figsize=(8.5, 8.5*9/16))
plt.title(r'Rise time estimates without asymptotes in function of the damping ratio $\zeta$')
plt.plot(ζ, ζ * slope - t_r, label=r'True numerical solution: $2\log \left(9\right) \zeta - t_r\omega_n$', linewidth=1)
plt.plot(ζ, ζ * slope - approx, 'r', label=r'Approximation: $2\log \left(9\right) \zeta - \hat{t}_r\omega_n$', linewidth=1)
plt.xlim([1, ζ[-1]])
plt.xlabel(r'$\zeta$')
plt.ylabel(r'$2\log \left(9\right) \zeta - t_r \cdot \omega_n$')
plt.legend()
plt.tight_layout()
plt.savefig(path.join(path.dirname(sys.path[0]), 'images', 'risetime-overdamped-optimize.svg'))
plt.show()
