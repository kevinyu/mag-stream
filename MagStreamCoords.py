import numpy as np
import ephem

coords = []

b1 = np.arange(-90,-74,2)
b2 = np.arange(-88,-58,2)
lon1 = [-90, 45]
lon2 = [45,90]
dl1 = 2./(np.cos(np.deg2rad(b1)))
dl2 = 2./(np.cos(np.deg2rad(b2)))

for i in range(len(b1)):
    b = b1[i]
    dl = dl1[i]
    if b == -90:
        coords.append((0.0, b))
    else:
        next_l = lon1[0]
        coords.append((next_l, b))
        while next_l <= lon1[1]:
            next_l = next_l + dl
            coords.append((next_l, b))

for i in range(len(b2)):
    b = b2[i]
    dl = dl2[i]
    next_l = lon2[0]
    coords.append((next_l, b))
    while next_l <= lon2[1]:
        next_l = next_l + dl
        coords.append((next_l, b))

Glon = []
Glat = []
RA = []
DEC = []

for lon,lat in coords:
    g = ephem.Galactic(lon,lat,epoch='2000')
    Glon.append(g.lon)
    Glat.append(g.lat)
    eq = ephem.Equatorial(g)
    RA.append(np.rad2deg(eq.ra))
    DEC.append(np.rad2deg(eq.dec))

np.savez('MagStreamCoords.npz', ra=RA, dec=DEC, lon=Glon, lat=Glat)