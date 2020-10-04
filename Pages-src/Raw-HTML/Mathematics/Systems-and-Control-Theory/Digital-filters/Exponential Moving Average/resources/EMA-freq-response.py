from scipy.signal import freqz 
import matplotlib.pyplot as plt
from math import pi, acos
import numpy as np

alpha = 0.25

b = np.array(alpha)
a = np.array((1, alpha - 1))

print("b =", b)                        # Print the coefficients
print("a =", a)

x = (alpha**2 + 2*alpha - 2) / (2*alpha - 2)
w_c = acos(x)                          # Calculate the cut-off frequency

w, h = freqz(b, a)                     # Calculate the frequency response

plt.subplot(2, 1, 1)                   # Plot the amplitude response
plt.suptitle('Bode Plot')            
plt.plot(w, 20 * np.log10(abs(h)))     # Convert to dB
plt.ylabel('Magnitude [dB]')
plt.xlim(0, pi)
plt.ylim(-18, 1)
plt.axvline(w_c, color='red')
plt.axhline(-3, linewidth=0.8, color='black', linestyle=':')

plt.subplot(2, 1, 2)                   # Plot the phase response
plt.plot(w, 180 * np.angle(h) / pi)    # Convert argument to degrees
plt.xlabel('Frequency [rad/sample]')
plt.ylabel('Phase [°]')
plt.xlim(0, pi)
plt.ylim(-90, 90)
plt.yticks([-90, -45, 0, 45, 90])
plt.axvline(w_c, color='red')
plt.show()