#!/usr/bin/env python
import ephem
import numpy as np
import argparse

# Import dish control modules
import dish
import dish_synth
import takespec

def main():
    """Records 1 minute of test data from the Leuschner dish.
    """
    parser = argparse.ArgumentParser(description='Record test data from the dish.')
    parser.add_argument('--home', action='store_true', default=False,
            help='run homing routine (warning, takes a few minutes)')
    parser.add_argument('--verbose', action='store_true', default=True,
            help='print verbose output')
    parser.add_argument('--lon', type=float, default=220,
            help='LO frequency.')
    args = parser.parse_args()

    # Set lat and long (for Leuschner from Google Maps), and date
    obs = ephem.Observer()
    obs.lat = 37.919481 * np.pi/180
    obs.long = -122.153435 * np.pi/180

    # Compute number of spectra to record (integration time=1 min)
    length = 60             # integration time in seconds
    num_spec = length/3

    print 'Observing galactic coordinates long=%s, lat=0'%(str(args.lon))
    point_gal= ephem.Galactic(args.lon*np.pi/180, 0)
    point_eq= ephem.Equatorial(point_gal)

    # Compute az alt
    point = ephem.FixedBody()
    point._ra = point_eq.ra
    point._dec = point_eq.dec

    # Create synthesizer interface
    s = dish_synth.Synth(verbose=args.verbose)
    s.set_freq(1272.4) # frequency in MHZ
    s.set_amp(10) # amplitude in dbM

    # Create dish interface
    d = dish.Dish(verbose=args.verbose)
    d.noise_off()
    if args.home:
        d.home()

    obs.date = ephem.now()
    point.compute(obs)
    print 'RA: '+str(point.ra)
    print 'DEC: '+str(point.dec)
    d.point(point.alt*180/np.pi, point.az*180/np.pi)

    # Record spectra noise off
    takespec.takeSpec('test_'+str(args.lon)+'_0_noise_off', numSpec=num_spec)

    d.noise_on()

    # Record spectra noise on
    takespec.takeSpec('test_'+str(args.lon)+'_0_noise_on', numSpec=num_spec)

    # Record spectra with LO set 4MHz lower and noise off
    s.set_freq(1268.4) # frequency in MHZ
    d.noise_off()
    takespec.takeSpec('test_'+str(args.lon)+'_0_noise_off_low', numSpec=num_spec)

if __name__ == "__main__":
    main()
