import numpy as np


all_points = np.load("../code/coordinates.npz")


import matplotlib.pyplot as plt
from imager import *

# size of the shit
SIZE = 401

plt.figure(figsize=[6.175, 10.2])

# the image grid
grid = np.zeros((SIZE, SIZE))


THETA = np.deg2rad(all_points["lon"])
R = np.cos(np.deg2rad(all_points["lat"]))
X = R * np.cos(THETA)
Y = R * np.sin(THETA)
Z = all_points["N"]

XMAX = 0.6
YMAX = 0.6

for x, y, z in zip(X, Y, Z):
    ix = int(round(SIZE * (x/ XMAX)))
    iy = int(round(SIZE * (y/ YMAX)))
    grid[iy][ix] = z * 120

new = make_a_fucking_image(grid)
im = plt.imshow(new, cmap="Oranges")



ylim(reversed(ylim()))

def circ(x, r):
    return np.sqrt(r**2 - x**2)

xspace = np.linspace(xlim()[0], xlim()[1], 100000)
plt.plot(xspace, circ(xspace, SIZE * np.cos(np.deg2rad(-75.))/YMAX), "k:")
plt.plot(xspace, circ(xspace, SIZE * np.cos(np.deg2rad(-60.0))/YMAX), "k:")

xlim(0, 200)
# plt.plot(xlim(), xlim(), "w-")
plt.plot(xlim(), map(lambda x: x * (1.732), xlim()), "k:")
plt.plot(xlim(), map(lambda x: x * (0.5773), xlim()), "k:")

xticks([])
locs, labels = plt.xticks()
plt.xticks(locs, map(lambda x: r"$%d^\circ$" % (-90 + np.rad2deg(float(x)/float(SIZE) * 0.6)) , locs), fontsize=16)

yticks([0, 172, 334])
locs, labels = plt.yticks()
plt.yticks(locs, [r"$-90^\circ$", r"$-75^\circ$", r"$-60^\circ$"], fontsize=16)
# plt.imshow(grid)

ylabel(r"$\mathrm{Galactic\ Latitude\ (b)}$", fontsize=20, labelpad=0)

ax = gca()
ax.tick_params(right="off")

from mpl_toolkits.axes_grid1 import make_axes_locatable
divider = make_axes_locatable(ax)
cax = divider.append_axes("bottom", size="5%", pad=0.05)
thecolorbar = plt.colorbar(im, orientation="horizontal", cax=cax)


thecolorbar.set_ticks([0, 200, 400, 600, 800])
thecolorbar.set_label(r"$\mathrm{Integration\ Time\ [s]}$", fontsize=16, labelpad=20)

ax.text(-10, 405, r"$l=+90^\circ$", fontsize=14)
ax.text(202, 340, r"$l=+60^\circ$", fontsize=14)
ax.text(202, 110, r"$l=+30^\circ$", fontsize=14)
ax.text(202, -5, r"$l=0^\circ$", fontsize=14)


def get_subplotpars(fig=1):
    a = figure(fig)
    terms = ["top", "bottom", "left", "right", "hspace", "wspace"]
    return dict((term, getattr(a.subplotpars, term)) for term in terms)


subplots_adjust(**{'bottom': 0.1,
 'hspace': 0.2,
 'left': 0.125,
 'right': 0.9,
 'top': 0.9,
 'wspace': 0.2})


"""
# points plot
plt.figure()
ax = plt.subplot(111, polar=True)
# ax.grid(True)
ax.set_yticks(np.arange(-90, 0, 15))
ax.set_yticklabels(map(str, range(-90, 0, 15)))   # Change the labels
ax.plot(np.deg2rad(all_points["lon"]), all_points["lat"], "b-", marker="o")
ax.set_rmax(-58)

# other
# plt.figure()
# ax = plt.subplot(111, polar=True)
# ax.grid(True)

longlats = read_data.specs.keys()
lon, lat = zip(*longlats)
lon = np.array(lon)
lat = np.array(lat)
ax.plot(np.deg2rad(lon), lat, "ro", markersize=10, markeredgecolor="r", alpha=0.5)
# ax.set_rmax(0.6)
"""
