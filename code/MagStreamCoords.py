import numpy as np
import ephem

coords = []

b1 = np.arange(-90,-74,2)
b2 = np.arange(-90,-58,2)
lon1 = [-90, 90]
lon2 = [66,90]
# lon3 = [-90, -45]
dl1 = 2./(np.cos(np.deg2rad(b1)))
dl2 = 2./(np.cos(np.deg2rad(b2)))

for i in range(len(b2)):
    b = b2[i]
    dl = dl2[i]
    if b == -90:
        coords.append((0.0, b))
    else:
        if b <= -75:
            next_l = lon1[0]
            while next_l <= lon1[1]:
                coords.append((next_l, b))
                next_l = next_l + dl
        else:
            next_l = lon2[0]
            while next_l <= lon2[1]:
                coords.append((next_l, b))
                next_l = next_l + dl
            '''
            # This part includes some extra stuff
            next_l = lon3[0]
            while next_l <= lon3[1]:
                coords.append((next_l, b))
                next_l = next_l + dl
            '''

Glon = []
Glat = []
RA = []
DEC = []

for lon,lat in coords:
    g = ephem.Galactic(np.deg2rad(lon), np.deg2rad(lat), epoch='2000')
    Glon.append(np.rad2deg(g.lon))
    Glat.append(np.rad2deg(g.lat))
    eq = ephem.Equatorial(g)
    RA.append(np.rad2deg(eq.ra))
    DEC.append(np.rad2deg(eq.dec))


# sort it into a logical order
sorted_by_lat = sorted(zip(Glat, Glon, DEC, RA, [0] * len(DEC), [0.0] * len(DEC)))
from itertools import groupby
new_world_order = []
reverse = False
for lat, row in groupby(sorted_by_lat, lambda r: r[0]):
    new_world_order += sorted(list(row), key=lambda r: r[1], reverse=reverse)
    reverse = not reverse

Glat, Glon, DEC, RA, N, t_obs = zip(*new_world_order)

np.savez('coordinates.npz', ra=RA, dec=DEC, lon=Glon, lat=Glat, N=N, t_obs=t_obs)

# also save a copy here that won't be touched by the code
np.savez('_coordinates.npz', ra=RA, dec=DEC, lon=Glon, lat=Glat, N=N, t_obs=t_obs)
