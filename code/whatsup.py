"""
Script for showing where an array of RA, DEC coordinates are in the sky at a certain time
Observer location is hard-coded to (LONG, LAT): (-122.2573 deg, 37.8732 deg)

Positional Argument:
    A .npz file containing an "ra" and "dec" array for the grid of points (J2000). Make sure its in DEGREES.

Optional Argument:
    --time : A string in the form "mm-dd-yyyy HH:MM:SS". If not given, the script defaults to showing the points as they currently appear in the sky

Output:
    Plot of the grid of points provided in (az, alt) in degrees. Shaded region is where the telescope is out of range.

example usage:
$ python whatsup.py coordinates.npz --time="04-25-2014 12:00:00"

"""

import numpy as np
import argparse
import datetime
import ephem

import matplotlib.pyplot as plt


LONG = -122.2573  # deg
LAT = 37.8732  # deg
obs = ephem.Observer()
obs.long = np.deg2rad(LONG)
obs.lat = np.deg2rad(LAT)

ALT_LIMITS = np.loadtxt('alt_limits.txt')

plt.figure()
def show(coords, time):
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Show location of points in the sky')
    parser.add_argument('coords_file', help='path to .npz file with "ra" and "dec" arrays')
    parser.add_argument('--time', type=str, default="", help='time to check in form "mm-dd-yyyy HH:MM:SS"')
    args = parser.parse_args()

    show(np.load(args.coords_file), time=args.time)
