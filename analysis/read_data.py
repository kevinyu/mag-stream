"""
Set the "data" directory before using this

If you import this file, you get the variables:
    freqs: frequency array for the averaged and normalized spectra
    specs: dictionary of (l, b) to spectra array
    peaks: dictionary of (l, b) to peak of 21cm line of that point's spectra
    vels: dictionary of (l, b) to velocity in km/s of that point

"""

import numpy as np
import glob
import os

data_dir = "play_data"

F_OFF = 1269.6
F_ON = 1273.6
point_dirs = glob.glob(os.path.join(data_dir, "*"))

C = 299792458.                   # Speed of light in m/s
LAMBDA_H1 = 0.2110611405413     # Wavelength of H1 emissions in m
NU_H1 = C / LAMBDA_H1
km = 1000.


def clean_spec(on, on_n, off, off_n):
    count = len(on)  # 8192

    # the (relative) gain at each frequency
    gain_on = (on_n - on)
    gain_off = (off_n - off)

    on = on / gain_on
    off = off / gain_off

    # the overall shape without the spectral features should be the first half
    # of the data for the LO off (lower) and the second half for the LO on (higher)
    shape = np.append(off[:count/2], on[count/2:])

    # subtract the overall shape from the data
    on = on - shape
    off = off - shape

    # cut off the ends (-2731 is int((4 MHz / 12 MHz)*count) )
    zee_result = ((on[:-2731] + off[2731:]) / 2.)[count/2 - 2731:count/2]

    return zee_result


specs = dict()
for point_dir in point_dirs:
    array_files = glob.glob(os.path.join(point_dir, "*.npz"))
    coord = None
    N = 0  # number averaged
    for array_file in array_files:
        arr = np.load(array_file)
        if coord and coord != (float(arr["l"]), float(arr["b"])):
            raise Exception("coordinates dont match within one pointing directory")
        coord = (float(arr["l"]), float(arr["b"]))
        noise = bool(arr["noise"])
        lo_on = float(arr["lo"]) == F_ON

        if lo_on and not noise:
            on = arr["spec"]
            N += arr["N"]
        elif lo_on and noise:
            on_noise = arr["spec"]
        elif not lo_on and not noise:
            off = arr["spec"]
            N += arr["N"]
        elif not lo_on and noise:
            off_noise = arr["spec"]

    result = clean_spec(on, on_noise, off, off_noise)

    if coord not in specs:
        specs[coord] = (N, result)
    else:
        old_N = specs[coord][0]
        specs[coord] = (old_N * specs[coord][1] + N * result)  / (old_N + N)


specs = dict((coord, spec) for coord, (N, spec) in specs.items())

count = 8192
# freqs = np.linspace(F_ON + 150 - 6, F_ON + 150 + 2, count-2731)[count/2 - 2731:count/2]
# this line is for the sample F_ON
freqs = np.linspace(1272.4 + 150 - 6, 1272.4 + 150 + 2, count-2731)[count/2 - 2731:count/2]


def peak2v(peak_f):
    """Convert a 21cm line detection frequency to a relative velocity in km/s"""
    return (((NU_H1 - peak_f * 1e6) / NU_H1) * C) / km

def peakfinder(spec):
    """Find peak frequency for spectra"""
    # TODO: put more robust peak-finding code here
    return freqs[np.argmax(spec)]


peaks = dict((coord, peakfinder(spec)) for coord, spec in specs.items())
vels = dict((coord, peak2v(peak)) for coord, peak in peaks.items())
