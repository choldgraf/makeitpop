import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from colorspacious import cspace_converter
import numpy as np
import pandas as pd

_sRGB1_to_uniform = cspace_converter("sRGB1", "CAM02-UCS")


def _calculate_derivatives(cmap):
    if isinstance(cmap, str):
        cmap = plt.get_cmap(cmap)

    if isinstance(cmap, ListedColormap) and cmap.N >= 100:
        RGB = np.asarray(cmap.colors)[:, :3]
        N = RGB.shape[0]
        x = np.linspace(0, 1, N)
    else:
        N = 256
        x = np.linspace(0, 1, N)
        RGB = cmap(x)[:, :3]
    Jpapbp = _sRGB1_to_uniform(RGB)
    deltas = np.sqrt(np.sum((Jpapbp[:-1, :] - Jpapbp[1:, :]) ** 2, axis=-1))
    derivs = N * deltas

    derivs = np.hstack([np.mean(derivs), derivs])
    deltas = np.hstack([np.mean(deltas), deltas])
    return deltas, derivs, x


def update_derivatives(cmaps):
    derivatives = {}
    for cmap in cmaps:
        this_deltas, this_derivs, x = _calculate_derivatives(cmap)

        # Scale the derivatives
        derivatives[cmap] = this_derivs

    # Collect
    derivatives = pd.DataFrame(derivatives, index=pd.Series(x, name='x'))

    # Scale by derivatives variance
    derivatives_scaled = (derivatives - derivatives.mean()) / derivatives.std().max()
    # Scale between 0 and 1
    derivatives_scaled = derivatives_scaled / np.max(np.abs(derivatives_scaled)).max()

    return derivatives, derivatives_scaled
