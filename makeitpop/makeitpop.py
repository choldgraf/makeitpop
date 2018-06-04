from scipy.interpolate import interp1d
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.pyplot as plt
import numpy as np
from .derivatives import update_derivatives

cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'PuBuGn', 'YlGnBu',
         'spring', 'summer', 'autumn', 'winter', 'hot', 'cool',
         'hsv', 'rainbow', 'jet']

derivatives, derivatives_scaled = update_derivatives(cmaps)


def makeitpop(data, colormap='jet', scaling_factor=20, invert=False):
    """Make your data pop!

    Non-linearly scaled a dataset according to the perceptual warping that
    is performed by a colormap. NOTE: YOU SHOULD NEVER DO THIS IN REAL LIFE.
    This is simply an attempt to illustrate more clearly what happens when 2-D
    data is visualized with colormaps that don't have a constant perceptual delta
    across values. For more information, see https://bids.github.io/colormap/

    Inputs
    ------
    data : numpy array
        The data you'd like to make more sexy.
    colormap : string | array, shape (n_derivatives,)
<<<<<<< HEAD
        The colormap you'd like to use to warp your data. Assume to be a
        string that will index into `makeitpop.scaled_derivatives`.
    scaling_factor : int
        Higher values will accentuate the "popping" effect.
=======
        The colormap you'd like to use to warp your data. If a string, this will
        index into `makeitpop.scaled_derivatives`. If an array, it is assumed to
        be the scaled derivatives of a colormap, where the first value corresponds
        to x == 0, and the last value to x == 1.
>>>>>>> a64c0c72e739f09ea1194bffe0a2fceb07127f9c
    invert : bool
        Whether to invert the perceptual warping function of the colormap.

    Returns
    -------
    data_new : numpy array, shape data.shape
        The input data after being altered according to the perceptual warping
        for the colormap of your choice!
    """
    if data.ndim == 1:
        data = data[:, None]

    # The popper will take 0-1 values and map them onto the colormap's delta function 0-1 values
    popper = pop_like(colormap, scaling_factor=scaling_factor, invert=invert)

    # Scale so that we're between 0 and 1
    scaler = MinMax()
    data_norm = scaler.fit_transform(data)

    # Warp this CDF onto the one for the colormap we're using to pop
    data_norm_popped = popper(data_norm)

    # Create sexier data
    data_new = scaler.inverse_transform(data_norm_popped)
    data_new = data_new.reshape(data.shape)
    return data_new.squeeze()


def pop_like(colormap, scaling_factor=20, invert=False):
    """
    Parameters
    ----------
    colormap : string
        The colormap into which we'd like to warp our data.

    Returns
    -------
    popper : function
        A function that maps 0 to 1 values onto the 0 to 1
        values of new_map.
    """
    # Figure out the "true" y values for linear x inputs
    x = np.linspace(0, 1, 256)
    y_true = x.copy()
    derivatives_true = y_true[1] - y_true[0]

    # Now warp the y-values so their derivatives that of our perceptual deltas
    derivatives_warp = derivatives_scaled[colormap] * scaling_factor
    if invert is True:
        derivatives_warp = derivatives_warp * -1

    # This tells us how much the linear derivs should be changed to make them warped
    derivatives_warped_diffs = derivatives_warp * derivatives_true

    y_warped = y_true + derivatives_warped_diffs
    popper = interp1d(x, y_warped)
    return popper


class MinMax(object):
    def __init__(self):
        pass

    def fit_transform(self, values):
        self.min = values.min()
        self.max = values.max()
        scaled = (values - self.min) / (self.max - self.min)
        return scaled

    def inverse_transform(self, values):
        if self.min is None:
            raise ValueError("You need to fit first!")
        return (values * (self.max - self.min)) + self.min
