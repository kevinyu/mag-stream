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

data_dir = "/home/kyu/somebetterdatas/"
data_dir = "../data"

F_OFF = 1269.6
F_ON = 1273.6
point_dirs = glob.glob(os.path.join(data_dir, "*"))

C = 299792458.                   # Speed of light in m/s
LAMBDA_H1 = 0.2110611405413     # Wavelength of H1 emissions in m
NU_H1 = C / LAMBDA_H1
km = 1000.

count = 8192
# this line is for the sample F_ON
# freqs = np.linspace(1272.4 + 150 - 6, 1272.4 + 150 + 2, count-2731)[count/2 - 2731:count/2]
freqs_full = np.linspace(F_ON + 150 - 6, F_ON + 150 + 6, count)
freqs_full_off = np.linspace(F_OFF + 150 - 6, F_OFF + 150 + 6, count)
freqs_on = np.linspace(F_ON + 150 - 6, F_ON + 150 + 2, count-2731)[count/2 - 2731:count/2]
freqs_off = np.linspace(F_OFF + 150-2, F_OFF + 150 + 6, count-2731)[count/2 - 2731:count/2]


def get_selector(frequencies):
    return np.where(( (1*(1419.5 < frequencies)) * (1*(frequencies < 1420.2)) ) | ((1*(1423. < frequencies))  * (1 * (frequencies < 1424.5)) ))


def calibrate(on, on_n, off, off_n):
    """get over it"""
    return on, on_n, off, off_n


def el_boxcar(x, width):
    medianed = np.zeros(len(x))
    x = list(x)
    for i in range(len(x)):
        boxcar = x[max(0, i-width/2):i+width/2]
        medianed[i] = np.median(boxcar)
    return medianed


from collections import defaultdict

specs = defaultdict(list)
for point_dir in point_dirs:
    array_files = glob.glob(os.path.join(point_dir, "*.npz"))
    coord = None
    N = 0  # number averaged
    for array_file in array_files:
        arr = np.load(array_file)
        # if coord and coord != (float(arr["l"]), float(arr["b"])):
        #     raise Exception("coordinates dont match within one pointing directory")
        coord = (float(arr["l"]), float(arr["b"]), array_file)
        coord = (float(arr["l"]), float(arr["b"]))
        noise = bool(arr["noise"])
        lo_on = float(arr["lo"]) == F_ON

        if lo_on and not noise:
            on = el_boxcar(arr["spec"], 10)
            # on = arr["spec"]
            N += arr["N"]
        elif lo_on and noise:
            on_noise = el_boxcar(arr["spec"], 10)
            # on_noise = arr["spec"]
        elif not lo_on and not noise:
            off = el_boxcar(arr["spec"], 10)
            # off = arr["spec"]
            N += arr["N"]
        elif not lo_on and noise:
            # off_noise = arr["spec"]
            off_noise = el_boxcar(arr["spec"], 10)

    # not actually calibrate, just dont want to change the function name
    result = calibrate(on, on_noise, off, off_noise)
    specs[coord].append((N, result))

    print "done with", coord


import pickle
specs = dict(specs)
pickle.dump(specs, open("specs.pkl", "wb"))
