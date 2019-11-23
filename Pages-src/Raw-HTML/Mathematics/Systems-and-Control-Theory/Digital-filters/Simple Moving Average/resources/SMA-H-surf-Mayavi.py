#!/usr/bin/env python3

import mayavi.mlab as mlab
import numpy as np
import os

script_dir = os.path.dirname(os.path.realpath(__file__))

N = 9

max = 15
min = -60

# Make H surface
X = np.linspace(-1.5, 1.5, 1024 * 5)
Y = np.linspace(-1.5, 1.5, 1024 * 5)
X, Y = np.meshgrid(X, Y)
z = X + Y * 1j
Z = 1 / N * np.abs(1 - z**-N) / np.abs(1 - 1 / z)
Z = 20 * np.log10(Z)
Z[np.logical_or(Z > max, Z < min)] = np.nan
Z = Z / 40 + 0.6

# Make the image of the unit circle
omega = np.linspace(2 * np.pi / 2048, 2 * np.pi - 2 * np.pi / 2048, 2047)
circ_X = np.cos(omega)
circ_Y = np.sin(omega)
circ_Z = 1 / N * np.sin(N * omega / 2) / np.sin(omega / 2)
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

view = (90.0, 60, 5, (0, 0, 0))
mlab.view(*view, reset_roll=True)

from matplotlib import pyplot as plt

mlab.savefig(
    os.path.join(os.path.dirname(script_dir), f'images/SMA-H-surf-N{N}.png'))