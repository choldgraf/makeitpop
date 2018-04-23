from sklearn.preprocessing import MinMaxScaler
from scipy.interpolate import interp1d
import numpy as np
from .derivatives import update_derivatives

cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'PuBuGn', 'YlGnBu',
         'spring', 'summer', 'autumn', 'winter', 'hot', 'cool',
         'hsv', 'rainbow', 'jet']

derivatives, derivatives_scaled = update_derivatives(cmaps)


def makeitpop(data, colormap='jet', scaling_factor=1., invert=False):
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
        The colormap you'd like to use to warp your data. If a string, this will
        index into `makeitpop.scaled_derivatives`. If an array, it is assumed to
        be the scaled derivatives of a colormap, where the first value corresponds
        to x == 0, and the last value to x == 1.
    scaling_factor : float
        How much you'd like to exaggerate the warping of your data. If you want
        your results to look super publishable, increase this number.
    invert : bool
        Whether to invert the perceptual warping function of the colormap.
    """
    if data.ndim == 1:
        data = data[:, None]
        
    if isinstance(colormap, str):
        x = derivatives_scaled.index
        derivatives = derivatives_scaled[colormap]
    elif isinstance(colormap, np.ndarray):
        x = np.linspace(0, 1, len(colormap))
        derivatives = colormap

    # The popper will take 0-1 values and map them onto the colormap's delta function 0-1 values
    popper = pop_map(colormap)
    
    
    # Scale so that we're between 0 and 1
    scaler = MinMaxScaler()
    data_norm = scaler.fit_transform(data.reshape(-1, 1))
    data_popped = popper(data_norm)
    
    # Create sexier data
    data_new = scaler.inverse_transform(data_popped)
    data_new = data_new.reshape(data.shape)
    return data_new.squeeze()


def _inverse_cdf(values):
    # Turn into an iCDF
    cdf = values.cumsum()
    cdf = cdf / cdf[-1]
    
    if cdf[0] != 0:
        cdf = np.hstack([0, cdf])  # add 0 so we can interp
    icdf = interp1d(cdf, np.linspace(0, 1, len(cdf)))
    return icdf


def pop_map(new_cmap, old_cmap='linear'):
    """
    Parameters
    ----------
    new_cmap : string
        The colormap into which we'd like to warp our data.
    old_cmap : string
        The reference colormap we assume our data is currently in.
        This defaults to "linear" which assumes a perfectly perceptually
        flat colormap.
        
    Returns
    -------
    popper : function
        A function that maps 0 to 1 values onto the 0 to 1
        values of new_map.
    """
    # Find derivatives for each map
    deltas_orig = derivatives[old_cmap].values
    deltas_new = derivatives[new_cmap].values

    # Turn into an iCDF
    cdf_orig = deltas_orig.cumsum()
    cdf_orig = cdf_orig / cdf_orig[-1]
    cdf_orig = np.hstack([0, cdf_orig])  # add 0 so we can interp

    cdf_new = deltas_new.cumsum()
    cdf_new = cdf_new / cdf_new[-1]

    # This maps quantiles (from 0 to 1) onto input values (which is also 0 to 1)
    icdf_orig = _inverse_cdf(deltas_orig)
    corrected_vals = icdf_orig(cdf_new)
    
    # Now a function that maps input 0-1 values onto "corrected" 0-1 values
    inputs = np.linspace(0, 1, len(corrected_vals))
    return interp1d(inputs, corrected_vals)
