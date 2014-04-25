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
###Generating Coordinates###
Running code/MagStreamCoords.py generates a new input file.

###Plotting spectra###
usage: code/plot_spectra.py [-h] [--center CENTER] [--title TITLE]
                       [--outfile OUTFILE]
                       files [files ...]

Plot .log files on the same plot.

positional arguments:
  files              .log files to plot (full file names). Ex: plot_test.py
                     file0.log file1.log file2.log ...

optional arguments:
  -h, --help         show this help message and exit
  --center CENTER    Center frequency for plot in MHz
  --title TITLE      Plot title
  --outfile OUTFILE  Output file name


###Plotting sample data###
Run example
This will plot sample measurements from raw/test/ with observations at 2 different LO frequencies both with and without the noise diode on.

###Main Observation Script###
code/ directory should be copied directly over onto leuschner
$ scp -r -p 31 code radiolab@leuschner.berkeley.edu:/home/radiolab/mag-stream

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

