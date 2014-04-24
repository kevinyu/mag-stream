mag-stream
==========

Magellanic Stream Project

Input file fields                                                            
  galactic (ephem.Galactic): galactic coordinates                          
  ra (ephem.Angle): right ascension (RA) of the point to observe           
  dec (ephem.Angle): declination (DEC) of the point to observe             
  epoch (ephem.Date): epoch with which RA and DEC were calculated          
  t_obs(float): seconds observed

USAGE: observe.py [-h] [--time TIME] [--repoint REPOINT] [--margin MARGIN]
                  [--verbose]
                  pointings_log

Record data from the Leuschner dish.

positional arguments:
  pointings_log      path to .npz file of points to observe

optional arguments:
  -h, --help         show this help message and exit
  --time TIME        integration time in seconds (defaults to 150s
  --repoint REPOINT  frequency of dish position updates
  --margin MARGIN    record point if it is within MARGIN degrees of the
                     altitude limit
  --verbose          additional debugging output

