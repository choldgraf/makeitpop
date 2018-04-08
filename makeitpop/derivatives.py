import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from colorspacious import cspace_converter
import numpy as np
import pandas as pd

_sRGB1_to_uniform = cspace_converter("sRGB1", "CAM02-UCS")

def _calculate_derivatives(cmap):
    if isinstance(cmap, str):
        cm = plt.get_cmap(cmap)

    if isinstance(cm, ListedColormap) and cm.N >= 100:
        RGB = np.asarray(cm.colors)[:, :3]
        N = RGB.shape[0]
        x = np.linspace(0, 1, N)
    else:
        N = 256
        x = np.linspace(0, 1, N)
        RGB = cm(x)[:, :3]
    Jpapbp = _sRGB1_to_uniform(RGB)
    deltas = np.sqrt(np.sum((Jpapbp[:-1, :] - Jpapbp[1:, :]) ** 2, axis=-1))
    derivs = N * deltas
    
    derivs = np.hstack([np.mean(derivs), derivs])
    deltas = np.hstack([np.mean(deltas), deltas])
    return deltas, derivs, x 

def update_derivatives(cmaps):
    derivs = {}
    for cmap in cmaps:
        this_deltas, this_derivs, x = _calculate_derivatives(cmap)

        # Scale the derivatives
        derivs[cmap] = this_derivs

    # Collect
    derivs = pd.DataFrame(derivs, index=pd.Series(x, name='x'))

    # Scale
    derivs_scaled = derivs.apply(lambda a: (a - np.mean(a)) / (np.max(derivs.values) - np.min(derivs.values)))
    derivs_scaled += 1
    return derivs, derivs_scaled 
