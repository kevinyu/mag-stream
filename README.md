mag-stream
==========

Magellanic Stream Project
==========

Directory Structure
----------
code- contains all code
raw- contains raw data files
raw/test- contains sample data

Usage Info
----------
###Scheduling Observations###
Run schedule
This script will schedule a cron job at a specified time.
This can be tested by running crontab -l and making sure that the appropriate
job shows up.

Any command line output (stdout, stderr) are logged in cronlog.

NOTE: currently the mag-stream directory on heiles isn't the same as the git
repository (may cause errors if you try to run schedule on a different
computer)

###Generating Coordinates###
Running code/MagStreamCoords.py generates a new input file.

###Plotting spectra###
Example: code/plot_spectra.py data/l77.6952_b-70.0000_04-29-2014_091705/ --median

usage: plot_spectra.py [-h] [--median] [--files FILES [FILES ...]]
                       [--center CENTER] [--title TITLE] [--outfile OUTFILE]
                       dir_name

Plot spectra.

positional arguments:
  dir_name              directory to plot. Ex: plot_spectra.py
                        data/l82.7631_b-80.0000_04-29-2014_092848/

optional arguments:
  -h, --help            show this help message and exit
  --median              Apply a length 5 median filter
  --files FILES [FILES ...]
                        .log files to plot (full file names). Ex: plot_test.py
                        file0.log file1.log file2.log ...
  --center CENTER       Center frequency for plot in MHz
  --title TITLE         Plot title
  --outfile OUTFILE     Output file name

###Plotting sample data###
Run example
This will plot sample measurements from raw/test/ with observations at 2 different LO frequencies both with and without the noise diode on.

###Main Observation Script###
entire code/ directory should be copied directly over onto leuschner for observation.
I had trouble scp-ing the directory from the lab computers;
instead, I sshed into leuschner and used scp from there. Ideally we don't have to do this again but if we do, just scp from leuschner.

Observation script must be run from within the code/ directory

usage: observe.py [-h] [--time TIME] [--repoint REPOINT] [--margin MARGIN]
                  [--verbose] [--endtime ENDTIME]
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
  --endtime ENDTIME  datetime string in form "mm-dd-yyyy hh:mm:ss"

