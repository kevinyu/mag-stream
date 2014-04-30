#!/usr/bin/env python
import sys
sys.path.append('/home/radiolab/ugradio/ugradio_code')
sys.path.append('/home/radiolab/mag-stream')

import logging
import os
import numpy as np
import time
import threading
import argparse
import ephem
import datetime

# Import dish control modules
import dish
import dish_synth
import takespec

import averager
import picker

PATH = '/home/radiolab/mag-stream'

V_MAX = -100000.                 # Maximum velocity m/s
V_MIN = -400000.                 # Minimum velocity m/s
C = 299792458.                   # Speed of light in m/s
LAMBDA_H1 = 0.2110611405413     # Wavelength of H1 emissions in m
NU_H1 = C / LAMBDA_H1

NU_MAX = NU_H1 * (1.0 - (V_MIN / C))
NU_MIN = NU_H1 * (1.0 - (V_MAX / C))

NU_MID = (NU_MAX + NU_MIN) / 2.0
NU_MID = 1421.6  # kevin: I just rounded it and write it here cuz its easier that way

LO_ON = NU_MID - 150 + 2
LO_OFF = LO_ON - 4

# Initialize Observer to lat and long for Leuschner (from Google Maps)
OBS = ephem.Observer()
OBS.lat = np.deg2rad(37.919481)
OBS.long = np.deg2rad(-122.153435)

ALT_LIMITS = np.loadtxt(os.path.join(PATH, 'alt_limits.txt'))

def init_log(log_name=os.path.join(PATH, 'logs', time.strftime("%m-%d-%Y_%H%M%S"))):
    """ Set up logging
    Args:
        log_name (String, optional): path and name of log file to be written
          (.log will be appended, default is in current working directory/logs)
    """

    FORMAT = '%(asctime)-15s - %(levelname)s: %(message)s'
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger('leuschner')
    #TODO(Vikram): check if this works when running from a different directory
    fh = logging.FileHandler(log_name+'.log')
    fh.setLevel(logging.DEBUG)

    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)

    formatter = logging.Formatter(FORMAT)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

def init_dish(noise=False, verbose=False):
    """Initializes an interface to the Leuschner dish and homes the dish
    (to zenith) to reset the encoders.

    Args:
        noise (bool, optional): True turns on the noise diode for calibration.
          Defaults to False.
        verbose (bool, optional): prints additional debugging output. Defaults
          to False.

    Returns:
        dish.Dish: Dish object representing the interface to the Leuschner dish
    """
    logger = logging.getLogger('leuschner')
    d = dish.Dish(verbose=verbose)

    if noise:
        logger.debug('Turning on noise diode')
        d.noise_on()

    else:
        logger.debug('Turning off noise diode')
        d.noise_off()

    d.home()
    logger.debug('Homing completed successfully')
    return d

def init_synth(freq=1390, amp=10, verbose=False):
    """Initializes the dish by setting the noise diode and homing the dish.

    Args:
        freq (float, optional): LO frequency (MHz).
        amp (float, optional): amplitude of sythesizer output (dBm)
        verbose (bool, optional): prints additional debugging output. Defaults
          to False.

    Returns:
        dish_synth.Synth: an interface to the synthesizer used to set the LO
          frequency
    """
    logger = logging.getLogger('leuschner')
    logger.debug('Creating synthesizer interface')
    s = dish_synth.Synth(verbose=verbose)
    logger.debug('Setting synth frequency to %s', str(freq))
    s.set_freq(freq)
    logger.debug('Setting synth amplitude to %s', str(amp))
    s.set_amp(amp)
    return s

def repoint(d, point, duration=300, repoint_freq=30.0):
    """Updates position and re-point telescope every t seconds.

    Args:
        d (dish.Dish): an interface to the Leuschner dish
        point (ephem.FixedBody): PyEphem fixed body object representing the
          coordinate on the sky to be observed
        repoint_freq (float, optional): number of seconds between updates.
          Defaults to 30.0 seconds.
    """
    logger = logging.getLogger('leuschner')
    t = 0
    while(t < duration):
        # Update the time and recompute position
        OBS.date = ephem.now()
        point.compute(OBS)
        logger.debug('Move to telescope to (alt, az): (%s,%s)',
                str(point.alt), str(point.az))
        try:
            d.point(np.rad2deg(point.alt), np.rad2deg(point.az))
        except ValueError, e:
            logger.error('Re-pointing failed for (alt,az): (%s,%s)',
                    str(getAlt(source)),
                    str(source.az))
            logger.error(str(e))

        except Exception, e:
            logger.error('Re-pointing failed for (alt,az): (%s,%s)',
                    str(getAlt(source)),
                    str(source.az))
            logger.error('Repointing failed: %s', str(e))
        time.sleep(repoint_freq)
        t += repoint_freq
    return

def record_pointing(d, s, l, b, point, file_name='raw/'+time.strftime("%m-%d-%Y_%H%M%S"),
        int_time=150, repoint_freq=30):
    """Records data from a point on the sky for a specified integration time.
    Spectra for an observation at two different LO frequencies and a separate
    10 second observation with the noise diode on are saved in the specified
    files.

    Args:
        d (dish.Dish): an interface to the Leuschner dish
        s (dish_synth.Synth): an interface to the synthesizer used to set the LO
          frequency
        file_name (String, optional): file name prefix to save the data
        int_time (float, optional): integration time (in seconds).
    """
    logger = logging.getLogger('leuschner')
    logger.debug('Recording data')
    status = 0

    # lets us keep data from this pointing in unique directory,
    # since each time we point we will have different noise/background spectrums
    record_id = time.strftime("%m-%d-%Y_%H%M%S")

    # Compute number of spectra to record (integration time/3)
    num_spec = int(int_time*3)
    num_spec_noise = 5 * 3

    OBS.date = ephem.now()
    point.compute(OBS)
    d.point(np.rad2deg(point.alt), np.rad2deg(point.az))

    # Take measurement with noise diode off at the higher LO frequency (ON frequency)
    s.set_freq(LO_ON)
    s.set_amp(10.0)
    d.noise_off()
    try:
        takespec.takeSpec(file_name+'_ON', numSpec=num_spec)
    except IOError:
        logger.error('%s not saved or averaged.' % (file_name+'_ON'))
        status = -1
    else:
        # Only want to average if the takespec was successful!
        averager.average(file_name+'_ON0.log', lo=LO_ON, l=l, b=b, record_id=record_id)

    # Take 10 second measurement with the noise diode on at the ON frequency
    d.noise_on()
    try:
        takespec.takeSpec(file_name+'_ON_noise', numSpec=num_spec_noise)
    except IOError:
        logger.error('%s not saved or averaged.' % (file_name+'_ON_noise'))
        status = -1
    else:
        averager.average(file_name+'_ON_noise0.log', lo=LO_ON, l=l, b=b, record_id=record_id, noise=True)

    # repoint for the second half of the measurement
    OBS.date = ephem.now()
    point.compute(OBS)
    d.point(np.rad2deg(point.alt), np.rad2deg(point.az))

    # Take 10 second measurement with the noise diode on at the OFF frequency
    s.set_freq(LO_OFF)
    s.set_amp(10.0)
    try:
        takespec.takeSpec(file_name+'_OFF_noise', numSpec=num_spec_noise)
    except IOError:
        logger.error('%s not saved or averaged.' % (file_name+'_OFF_noise'))
        status = -1
    else:
        averager.average(file_name+'_OFF_noise0.log', lo=LO_OFF, l=l, b=b, record_id=record_id, noise=True)

    d.noise_off()

    # Take measurement with noise diode off at the lower LO frequency (OFF frequency)
    s.set_freq(LO_OFF)
    s.set_amp(10.0)
    d.noise_off()
    try:
        takespec.takeSpec(file_name+'_OFF', numSpec=num_spec)
    except IOError:
        logger.error('%s not saved or averaged.' % (file_name+'_OFF'))
        status = -1
    else:
        averager.average(file_name+'_OFF0.log', lo=LO_OFF, l=l, b=b, record_id=record_id)

    logger.debug('Finished recording data')

def main():
    """
    Input file fields
        galactic (ephem.Galactic): galactic coordinates
        ra (ephem.Angle): right ascension (RA) of the point to observe
        dec (ephem.Angle): declination (DEC) of the point to observe
        epoch (ephem.Date): epoch with which RA and DEC were calculated
        t_obs(float): seconds observed
    """
    parser = argparse.ArgumentParser(description='Record data from the Leuschner dish.')
    parser.add_argument('pointings_log', help='path to .npz file of points to observe')
    parser.add_argument('--time', type=float, default=150,
            help='integration time in seconds (defaults to 150s')
    parser.add_argument('--repoint', type=float, default=30, help='frequency of dish position updates')
    parser.add_argument('--margin', type=float, default=2,
            help='record point if it is within MARGIN degrees of the altitude limit')
    parser.add_argument('--verbose', action='store_true', default=False,
            help='additional debugging output')
    parser.add_argument('--endtime', type=str, help='datetime string in form "mm-dd-yyyy hh:mm:ss"')
    args = parser.parse_args()

    if not os.path.exists(os.path.join(PATH, "raw")):
        os.mkdir(os.path.join(PATH, "raw"))
    if not os.path.exists(os.path.join(PATH, "logs")):
        os.mkdir(os.path.join(PATH, "logs"))
    if not os.path.exists(os.path.join(PATH, "data")):
        os.mkdir(os.path.join(PATH, "data"))

    if args.repoint <= 12:
        raise argparse.ArgumentTypeError("Can't repoint more often than every 12 seconds.")

    if args.time <= 0:
        raise argparse.ArgumentTypeError("Can't record for 0 seconds.")

    if not args.endtime:
        raise argparse.ArgumentError("Need to specify an endtime in the form 'mm-dd-yyyy hh:mm:ss'")

    logger = logging.getLogger('leuschner')

    init_log()
    pointings = np.load(os.path.join(PATH, args.pointings_log))

    logger.debug('Date: %s', str(OBS.date))
    logger.debug('Observer Latitude: %s', str(OBS.lat))
    logger.debug('Observer Long: %s', str(OBS.long))
    logger.debug('LO frequency: %s',  str(LO_ON))
    logger.debug('LO off frequency: %s',  str(LO_OFF))

    endtime = datetime.datetime.strptime(args.endtime, "%m-%d-%Y %H:%M:%S")

    # Create dish and synthesizer interfaces
    d = init_dish(verbose=args.verbose)
    s = init_synth(freq=LO_ON, amp=10.0, verbose=args.verbose)

    while datetime.datetime.now() + datetime.timedelta(seconds=2*args.time+10) <= endtime:
        in_range = False
        skip = 0
        max_N = 1
        while not in_range:
            if (datetime.datetime.now() + datetime.timedelta(seconds=2*args.time+10) > endtime):
                break
            # TODO (uh): the max_N=1 obvsiouly only works on the first run... what should we do?
            new_point = picker.pick(max_N=max_N, skip=skip)
            if type(new_point) == int:
                skip = 0
                max_N += 1
                continue

            ra = new_point['ra']
            dec = new_point['dec']
            # epoch = pointings['epoch']
            glat = new_point['lat']
            glon = new_point['lon']

            point = ephem.FixedBody()
            point._ra = np.deg2rad(ra)
            point._dec = np.deg2rad(dec)
            point._epoch = ephem.J2000  # kevin: Hardcoding this because I don't wanna deal with it
            OBS.date = ephem.now()
            point.compute(OBS)

            try:
                dish.pointing.az_alt_to_xy(np.rad2deg(point.az), np.rad2deg(point.alt) - args.margin)
            except ValueError:
                in_range = False
                logger.debug("Skipping (%s, %s) for due to reasons." % (np.rad2deg(point.az), np.rad2deg(point.alt)))
                skip += 1
                continue

            # Skip pointing if it isn't within the observing limits
            if (np.rad2deg(point.alt)-args.margin) <= ALT_LIMITS[int(np.rad2deg(point.az))]:
                in_range = False
                logger.debug("Skipping (%s, %s) for the greater good." % (np.rad2deg(point.az), np.rad2deg(point.alt)))
                skip += 1
            else:
                in_range = True
        if not in_range:
            break
        logger.debug("Picked next point %s" % new_point)
        logger.debug("Picked next point (alt, az): (%.4f, %.4f)" % (np.rad2deg(point.alt), np.rad2deg(point.az)))

        # CANT LAUNCH SEPARATE THREAD BECAUSE 2 THREADS CANT USE DISH
        # Create a thread that periodically re-points the telescope
        # Set the thread to run for 2*integration time + 5 seconds for initial
        # pointing
        # controller = threading.Thread(target = repoint,
        #         args = (d, point, args.time*2+5, args.repoint))
        # controller.daemon = True
        # controller.start()

        status = record_pointing(d, s, glon, glat, point,
            file_name=os.path.join(PATH, 'raw', 'l%.4f_b%.4f_%s' % (glon, glat, time.strftime("%m-%d-%Y_%H%M%S"))),
            int_time=args.time, repoint_freq=args.repoint)
        # controller.join()

        #TODO(Kevin): status will be -1 if data was not successfully saved
        picker.update(glon, glat, N=1, t_obs=args.time)

    logger.debug('Exiting')

if __name__ == "__main__":
    main()
