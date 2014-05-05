import matplotlib.pyplot as plt

import numpy as np

from astropy.convolution import convolve_fft, Gaussian2DKernel


def make_a_fucking_image(grid, kernelsize=50.):
    size = grid.shape[0]
    center = size/2
    kernel = Gaussian2DKernel(size/kernelsize, x_size=size, y_size=size)
    is_point = 1 * (grid > 0)
    weights = convolve_fft(is_point, kernel)
    invalid = np.where(weights < 0.00001)
    weights[invalid] = 1
    tha_result = convolve_fft(grid, kernel)
    tha_result[invalid] = 0
    return tha_result / weights
