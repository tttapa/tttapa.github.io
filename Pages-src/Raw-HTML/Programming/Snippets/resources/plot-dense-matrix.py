"""Plot a dense matrix using matplotlib, with special colors for zeros and
inf/nan. Useful for visualizing differences between matrices with possibly
missing values.w"""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def imshow_matrix(
    data,
    cmap: mcolors.Colormap | str | None = None,
    *,
    inf_color="red",
    zero_color="white",
):
    """Prepare data, colormap and normalization for imshow of a dense matrix.
    Zeros are shown as white, inf/nan as red (customizable)."""
    data = np.copy(data)
    min_val = np.min(data[np.isfinite(data) & (data > 0)])
    max_val = np.max(data[np.isfinite(data)])
    data[data == 0] = 0.99 * min_val
    cmap = plt.get_cmap(cmap).copy()
    cmap.set_bad(color=inf_color)  # inf/nan values
    cmap.set_under(color=zero_color)  # zero values
    norm = mcolors.LogNorm(vmin=min_val, vmax=max_val)
    return data, cmap, norm


import numpy as np

A = np.random.standard_normal((64, 96))
msk = np.random.uniform(0, 1, A.shape) > 0.5
np.fill_diagonal(A, np.nan)
A[msk] = 0
plt.imshow(*imshow_matrix(abs(A), cmap="viridis"))
plt.colorbar()
plt.show()
