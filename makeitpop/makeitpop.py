from sklearn.preprocessing import MinMaxScaler
from scipy.interpolate import interp1d
from .derivatives import update_derivatives

cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'PuBuGn', 'YlGnBu',
         'spring', 'summer', 'autumn', 'winter', 'hot', 'cool',
         'hsv', 'rainbow', 'jet']

derivatives, derivatives_scaled = update_derivatives(cmaps)


def makeitpop(data, colormap='jet', scaling_factor=1.):
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
    scaled_derivatives : pandas DataFrame created by "update_derivatives"
        The scaled derivative functions for several colormaps. Several defaults
        are provided by this package, but if you'd like """
    if data.ndim == 1:
        data = data[:, None]
        
    if isinstance(colormap, str):
        x = derivatives_scaled.index
        derivatives = derivatives_scaled[colormap]
    elif isinstance(colormap, np.ndarray):
        x = np.linspace(0, 1, len(colormap))
        derivatives = colormap
    
    # Interpolate between our color values
    ffit = interp1d(x, derivatives, kind='linear')
    
    # Scale so that we're between 0 and 1
    scaler = MinMaxScaler()
    data_norm = scaler.fit_transform(data.reshape(-1, 1))
    multipliers = ffit(data_norm).reshape(data.shape)
    
    # Apply the scaling factor
    multipliers_mean = multipliers.mean()
    multipliers = ((multipliers - multipliers_mean) * scaling_factor) + multipliers_mean
    
    # Create sexier data
    data_new = data * multipliers
    return data_new.squeeze()

