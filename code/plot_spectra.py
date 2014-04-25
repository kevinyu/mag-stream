#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import argparse
import readspec_mod

def plot_spectra(files, fc=1272.4+150, title='', outfile=None):
    f_range = np.linspace(fc-6, fc+6, 8192)

    for filename in args.files:
        spec = readspec_mod.readSpec(filename)
        plt.plot(f_range, np.mean(spec,1), label=filename.split('/')[-1].split('.')[0])
        plt.title(title)
        plt.xlabel('MHz')
        plt.legend()
    if outfile:
        plt.savefig(outfile+'.png')
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot .log files on the same plot.')
    parser.add_argument('files', nargs='+', help='.log files to plot (full file names). Ex: plot_test.py file0.log file1.log file2.log ...')
    parser.add_argument('--center', type=float, default=1272.4+150, help='Center frequency for plot in MHz')
    parser.add_argument('--title', default='', help='Plot title')
    parser.add_argument('--outfile', default=None, help='Output file name')
    args = parser.parse_args()

    plot_spectra(args.files, args.center, args.title, args.outfile)
