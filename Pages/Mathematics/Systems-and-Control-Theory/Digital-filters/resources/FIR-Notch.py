#!/usr/bin/env python3

from scipy.signal import butter, freqz 
import matplotlib.pyplot as plt
from math import pi, cos
import numpy as np

f_s = 360    # Sample frequency in Hz
f_c = 50     # Notch frequency in Hz

omega_c = 2 * pi * f_c       # Notch angular frequency
omega_c_d = omega_c / f_s    # Normalized notch frequency (digital)

h_0 = 2 - 2 * cos(omega_c_d)
b = np.array((1, -2 * cos(omega_c_d), 1))   # Calculate coefficients
b /= h_0                                    # Normalize
a = 1
print("a =", a)                      # Print the coefficients
print("b =", b)

w, h = freqz(b, a)                   # Calculate the frequency response
w *= f_s / (2 * pi)                  # Convert from rad/sample to Hz

plt.subplot(2, 1, 1)                 # Plot the amplitude response
plt.suptitle('Bode Plot')            
plt.plot(w, 20 * np.log10(abs(h)))   # Convert to dB
plt.ylabel('Magnitude [dB]')
plt.xlim(0, f_s / 2)
plt.ylim(-60, 20)
plt.axvline(f_c, color='red')

plt.subplot(2, 1, 2)                 # Plot the phase response
plt.plot(w, 180 * np.angle(h) / pi)  # Convert argument to degrees
plt.xlabel('Frequency [Hz]')
plt.ylabel('Phase [°]')
plt.xlim(0, f_s / 2)
plt.ylim(-90, 135)
plt.yticks([-90, -45, 0, 45, 90, 135])
plt.axvline(f_c, color='red')
plt.show()