import matplotlib.pyplot as plt
import numpy as np

f = 31250
R = 500_000
C1 = 0.1e-9
C2 = 0.5e-9
RC1 = R * C1
RC2 = R * C2
k_thres = 5
RC_thres = k_thres / f 
C_thres = RC_thres / R
print(RC1 * 1e6)
print(RC2 * 1e6)
print(RC_thres * 1e6)
print(C_thres * 1e9, 'nF')

N = 32
k = np.arange(N)
t = k / f
v1 = 5 * (1 - np.exp(-t / RC1))
v2 = 5 * (1 - np.exp(-t / RC2))

plt.figure(figsize=(5,4))
plt.plot(k, v1, '.-', label=r'$C_1=0.1 \mathrm{nF}$')
plt.plot(k, v2, '.-', label=r'$C_2=0.5 \mathrm{nF}$')
plt.axhline(0.632*5, linestyle='--', color='k', linewidth=1)
plt.axvline(k_thres, linestyle='--', color='k', linewidth=1)
plt.xlim([0, N-1])
plt.ylim([0, 5.5])
plt.xlabel(r'Time [samples at $31{,}250 \mathrm{Hz}$]')
plt.ylabel(r'Pin voltage [Volts]')
plt.title(r'Capacitive touch sensing $RC$-time threshold')
plt.text(N-4.5, 0.632*5*1.03, 'HIGH')
plt.text(N-4.5, 0.632*5*0.91, 'LOW')
plt.legend()
plt.savefig('rc.svg')
# plt.show()
