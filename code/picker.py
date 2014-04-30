import numpy as np


coordinates_file = "/home/radiolab/mag-stream/coordinates.npz"
coords = None


def pick(max_N=1, skip=0):
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
    global coords
    if not coords:
        coords = np.load(coordinates_file)

    # assume sorted by priority
    N_filter = coords["N"] < max_N
    filtered = np.sum(N_filter)
    if filtered == 0:
        # if nothing is less than the max_N, just use the ones with the smallest N
        max_N = np.min(coords["N"]) + 1
        N_filter = coords["N"] < max_N
        filtered = np.sum(N_filter)
    if filtered <= skip:
        # if we already have skipped everything, tell observe.py to increase max_N
        if max_N <= np.max(coords["N"]):
            return max_N + 1
        else:
            N_filter = np.array([True] * len(coords["N"]))
            skip = skip % len(coords["N"])

    return dict(
        ra=coords["ra"][N_filter][skip],
        dec=coords["dec"][N_filter][skip],
        lat=coords["lat"][N_filter][skip],
        lon=coords["lon"][N_filter][skip],
        N=coords["N"][N_filter][skip]
    )


# b is lat and l is long
def update(l, b, N=1, t_obs=1):
    """Increment a counter on coordinates (l, b) by N.

    N can be... # of samples averaged, or number of times observed. Whatever.
    We can also manipulate the N array later on to focus on certain points
    """
    global coords
    coords = None

    # cast to dict cuz you cant update the output of np.load
    coords = dict(np.load(coordinates_file))
    for i in range(len(coords["ra"])):
        if coords["lon"][i] == l and coords["lat"][i] == b:
            coords["N"][i] += N
    coords["t_obs"][i] += t_obs
    np.savez(coordinates_file, **coords)
