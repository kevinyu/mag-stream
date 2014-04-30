#!/usr/bin/env python
import numpy as np
import matplotlib.pyplot as plt
import argparse
import readspec_mod
import os
import glob
from scipy import signal

def plot_dir(dir_name, fc=1272.4+150, title='', median=False, outfile=None):
    f_range = np.linspace(fc-6, fc+6, 8192)
    print os.getcwd()+'/%s*.npz'%(dir_name)
    files = glob.glob(os.getcwd()+'/%s*.npz'%(dir_name))

    for filename in files:
        spec = np.load(filename)['spec']
        if median:
            spec = signal.medfilt(spec, 5)
        plt.plot(f_range, spec, label=filename.split('/')[-1].split('.')[0])
        plt.title(title)
        plt.xlabel('MHz')
        plt.legend()
    if outfile:
        plt.savefig(outfile+'.png')
    plt.show()

def plot_spectra(files, fc=1272.4+150, title='', median=False, outfile=None):
    f_range = np.linspace(fc-6, fc+6, 8192)

    for filename in files:
        spec = readspec_mod.readSpec(filename)
        plt.plot(f_range, np.mean(spec,1), label=filename.split('/')[-1].split('.')[0])
        plt.title(title)
        plt.xlabel('MHz')
        plt.legend()
    if outfile:
        plt.savefig(outfile+'.png')
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Plot spectra.')
    parser.add_argument('dir_name', help='directory to plot. Ex: plot_spectra.py data/l82.7631_b-80.0000_04-29-2014_092848/')
    parser.add_argument('--median', action='store_true', default=False,
            help='Apply a length 5 median filter')
    parser.add_argument('--files', nargs='+', default=None, help='.log files to plot (full file names). Ex: plot_test.py file0.log file1.log file2.log ...')
    parser.add_argument('--center', type=float, default=1272.4+150, help='Center frequency for plot in MHz')
    parser.add_argument('--title', default='', help='Plot title')
    parser.add_argument('--outfile', default=None, help='Output file name')
    args = parser.parse_args()

    if args.files:
        plot_spectra(args.files, args.center, args.title, args.median, args.outfile)

    else:
        plot_dir(args.dir_name, args.center, args.title, args.median, args.outfile)
