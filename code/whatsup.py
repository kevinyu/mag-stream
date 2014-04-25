import numpy as np
import datetime
import ephem

import matplotlib.pyplot as plt


coordinates_file = "coordinates.npz"

coords = np.load(coordinates_file)

LONG = -122.2573  # deg
LAT = 37.8732  # deg
obs = ephem.Observer()
obs.long = np.deg2rad(LONG)
obs.lat = np.deg2rad(LAT)

ALT_LIMITS = np.loadtxt('alt_limits.txt')

plt.figure()
def show(time=0.0):
    # print obs.date
    # alright boys here we go
    if time:
        dt = (datetime.datetime.strptime(time, "%m-%d-%Y %H:%M:%S") - datetime.datetime.now()).total_seconds()
    else:
        dt = 0.0

    obs.date = ephem.now()
    obs.date += dt / 86164.
    az = []
    alt = []
    for ra, dec in zip(coords["ra"], coords["dec"]):
        point = ephem.FixedBody()
        point._ra = np.deg2rad(ra)
        point._dec = np.deg2rad(dec)
        point._epoch = ephem.J2000
        point.compute(obs)
        az.append(point.az)
        alt.append(point.alt)

    az = np.array(az)
    alt = np.array(alt)

    plt.cla()
    plt.plot(np.rad2deg(az), np.rad2deg(alt), "-", marker="o")
    plt.fill_between(range(361), -45. * np.ones(361), ALT_LIMITS, color="Gray", alpha=0.2)
    plt.xlim(0, 360)
    plt.ylim(-15, 90)
    plt.show()


show()
