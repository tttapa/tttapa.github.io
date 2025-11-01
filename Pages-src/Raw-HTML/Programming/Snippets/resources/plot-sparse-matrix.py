"""Plot a sparse matrix using matplotlib, with special colors for structural
zeros, numerical zeros, and inf/nan. Useful for visualizing differences between
sparse matrices with possibly missing values."""

import numpy as np
import scipy.sparse as spa
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors


def nonzero_indices(matrix: spa.csc_array):
    """Get the indices of the structural nonzeros in the given sparse matrix"""
    minor = matrix.indices
    indptr = matrix.indptr
    major = np.repeat(np.arange(len(indptr) - 1, dtype=minor.dtype), np.diff(indptr))
    return minor, major


def plot_sparse_matrix(
    matrix: spa.csc_array,
    cmap: mcolors.Colormap | str | None = None,
    *,
    inf_color="red",
    struc_zero_color="lightgray",
    num_zero_color="white",
):
    """Prepare data, colormap and normalization for imshow of a sparse matrix.
    Structural zeros are shown as gray, numerical zeros as white, inf/nan as
    red (customizable)."""
    data = np.array(matrix.data, dtype=np.float64)
    fin_nonzero = np.logical_and(np.isfinite(data), data != 0)
    finite_data = abs(data[fin_nonzero])
    minval, maxval = np.min(finite_data, initial=1.0), np.max(finite_data, initial=1.0)
    margin = 2 * np.sqrt(maxval / minval)
    under, over = minval / margin, maxval * margin
    assert matrix.shape is not None
    dense_matrix = np.full(matrix.shape, under, order="F")
    rows, cols = nonzero_indices(matrix)
    data[data == 0] = over
    dense_matrix.ravel("K")[rows + cols * matrix.shape[0]] = data
    cmap = plt.get_cmap(cmap).copy()
    cmap.set_extremes(under=struc_zero_color, over=num_zero_color, bad=inf_color)
    norm = mcolors.LogNorm(vmin=float(minval), vmax=float(maxval))
    return dense_matrix, cmap, norm


A = np.random.standard_normal((64, 64))
np.fill_diagonal(A, np.nan)
sparse_A = spa.triu(A, format="csc")
msk = np.random.uniform(0, 1, sparse_A.data.shape) > 0.7
sparse_A.data[msk] = 0  # Introduce some numerical zeros
# Note: many scipy operations implicitly drop numerical zeros
plt.imshow(*plot_sparse_matrix(abs(sparse_A), cmap="viridis"))
plt.colorbar()
plt.show()
