import numpy as np
import time
import os
import readspec_mod


# where to put averaged data
DATA = "data"


def average(log_in, lo, l, b, noise=False, notes=None):
    """Averages spectra in a .log file and saves average to .npz with metadata

    Arguments:
        log_in: path to the .log file generated by takespec.takeSpec
        lo: lo frequency in MHz used
        l: galactic longitude of pointing, in degrees
        b: galactic latitude of pointing, in degrees
        noise (default=False): set to True if noise was turned on

    Puts averaged spectra into .npz file with following information
    "spec": averaged spectral data for each frequency bin
    "N": the number of spectra averaged
    "lo", "l", "b", "noise": the parameters passed in
    """
    # name the output directory by the galactic coords of the pointing
    pointing_dir = os.path.join(DATA, "l%.4f_b%.4f" % (l, b))
    if not os.path.exists(pointing_dir):
        os.makedirs(pointing_dir)

    # name the file according to the lo frequency + time so it doesnt get overwritten
    time_str = time.strftime("%m-%d-%Y_%H%M%S")

    output_filename = "%slo-%.1f_%s" % ("noise-" if noise else "", lo, time_str)
    spec_out = os.path.join(pointing_dir, output_filename)

    specs = readspec_mod.readSpec(log_in)
    averaged_spec = np.mean(specs, 1)
    np.savez(spec_out, spec=averaged_spec, lo=lo, N=specs.shape[0],
            l=l, b=b, noise=noise, notes=notes)
