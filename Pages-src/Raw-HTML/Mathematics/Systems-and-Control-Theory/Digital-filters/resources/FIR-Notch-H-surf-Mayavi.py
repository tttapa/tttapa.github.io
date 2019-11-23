#!/usr/bin/env python3

import mayavi.mlab as mlab
import numpy as np
import os

script_dir = os.path.dirname(os.path.realpath(__file__))

omega_c_d = 2 * np.pi * 50 / 360

max = 30
min = -60

# Make H surface
X = np.linspace(-1.5, 1.5, 1024 * 5)
Y = np.linspace(-1.5, 1.5, 1024 * 5)
X, Y = np.meshgrid(X, Y)
z = X + Y * 1j
alpha = -2 * np.cos(omega_c_d)
Z = np.abs(1 + alpha * z**-1 + z**-2) / (2 + alpha)
Z = 20 * np.log10(Z)
Z[np.logical_or(Z > max, Z < min)] = np.nan
Z = Z / 40 + 0.6

# Make the image of the unit circle
omega = np.linspace(2 * np.pi / 2048, 2 * np.pi - 2 * np.pi / 2048, 2047)
circ_X = np.cos(omega)
circ_Y = np.sin(omega)
z_circ = circ_X + circ_Y * 1j
circ_Z = np.abs(1 + alpha * z_circ**-1 + z_circ**-2) / (2 + alpha)
circ_Z = 10 * np.log10(circ_Z**2) + 0.1
circ_Z[np.logical_or(circ_Z > max, circ_Z < min)] = min
circ_Z = circ_Z / 40 + 0.6

# Plot the H surface and the unit circle
mlab.figure(size=(1080 * 2, 720 * 2),
            bgcolor=(1.0, 1.0, 1.0),
            fgcolor=(.6, .1, .1))
mlab.surf(-np.transpose(X),
          np.transpose(Y),
          np.transpose(Z),
          extent=[-1.5, 1.5, -1.5, 1.5, min / 40 + 0.6, max / 40 + 0.6],
          opacity=0.9,
          colormap='ocean')
mlab.plot3d(-circ_X, circ_Y, circ_Z, tube_radius=None)

view = (90, 60, 5, (0, 0, 0.3))
mlab.view(*view, reset_roll=True)

from matplotlib import pyplot as plt

mlab.savefig(
    os.path.join(os.path.dirname(script_dir), 'images/FIR-Notch-H-surf.png'))
