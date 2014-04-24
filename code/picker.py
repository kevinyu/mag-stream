import numpy as np


coordinates_file = "coordinates.npz"


def pick(max_N=1):
    """Pick the next coordinate with counter N less than max_N

    If all coordinates have counters greater than max_N, prioritize coordinates with lowest N?
    We should change this though to prioritize certain points

    Returns a dict with keys
        "ra"
        "dec"
        "lat": galactic latitude (b)
        "lon": galactic longitude (l)
        "N": counter
    """
    # assume sorted by priority
    coords = np.load(coordinates_file)
    for i in range(len(coords["ra"])):
        if coords["N"][i] < max_N:
            return dict(
                ra=coords["ra"][i],
                dec=coords["dec"][i],
                lat=coords["lat"][i],
                lon=coords["lon"][i],
                N=coords["N"][i]
            )

    # if everything has at least max_N, just start going by smallest N
    smallest_N = np.argmin(coords["N"])
    return dict(
        ra=coords["ra"][smallest_N],
        dec=coords["dec"][smallest_N],
        lat=coords["lat"][smallest_N],
        lon=coords["lon"][smallest_N],
        N=coords["N"][smallest_N]
    )


# b is lat and l is long
def update(l, b, N=1):
    """Increment a counter on coordinates (l, b) by N.

    N can be... # of samples averaged, or number of times observed. Whatever.
    We can also manipulate the N array later on to focus on certain points
    """
    # cast to dict cuz you cant update the output of np.load
    coords = dict(np.load(coordinates_file))
    for i in range(len(coords["ra"])):
        if coords["lon"][i] == l and coords["lat"][i] == b:
            coords["N"][i] += N
    np.savez(coordinates_file, **coords)
