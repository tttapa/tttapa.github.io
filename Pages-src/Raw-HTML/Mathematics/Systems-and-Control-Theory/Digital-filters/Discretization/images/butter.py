from scipy.signal import butter, freqz
import matplotlib.pyplot as plt
from math import pi
import numpy as np

f_s = 360    # Sample frequency in Hz
f_c = 45     # Cut-off frequency in Hz
order = 4    # Order of the butterworth filter

omega_c = 2 * pi * f_c       # Cut-off angular frequency
omega_c_d = omega_c / f_s    # Normalized cut-off frequency (digital)

b, a = butter(order, omega_c_d / pi)    # Design the Butterworth filter
print("a =", a)                         # Print the coefficients
print("b =", b)

w, h = freqz(b, a, 4096)             # Calculate the frequency response
w *= f_s / (2 * pi)                  # Convert from rad/sample to Hz

plt.subplot(2, 1, 1)                 # Plot the amplitude response
plt.suptitle('Bode Plot')
plt.plot(w, 20 * np.log10(abs(h)))   # Convert to dB
plt.ylabel('Magnitude [dB]')
plt.xlim(0, f_s / 2)
plt.ylim(-80, 6)
plt.axvline(f_c, color='red')
plt.axhline(-3, linewidth=0.8, color='black', linestyle=':')

plt.subplot(2, 1, 2)                 # Plot the phase response
plt.plot(w, 180 * np.angle(h) / pi)  # Convert argument to degrees
plt.xlabel('Frequency [Hz]')
plt.ylabel('Phase [°]')
plt.xlim(0, f_s / 2)
plt.ylim(-180, 180)
plt.yticks([-180, -135, -90, -45, 0, 45, 90, 135, 180])
plt.axvline(f_c, color='red')
plt.show()
