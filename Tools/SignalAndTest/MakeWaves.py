#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
File: MakeWaves.py
Generate wave data for plotting and creation of CSV data file
Designed for testing PlotCSV project FFT and Butterworth Filter custom scripts

References:
    How to generate a square wave
        https://pythontic.com/visualization/waveforms/squarewave
    See example to see how to generate and filter two sine waves added together
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.butter.html

"""

from scipy import signal
import matplotlib.pyplot as plot
import numpy as np
import datetime
import os


def scopy_export_header(local_nr, local_srate):
    """
    Generate first 7 lines of scopy export file
    :param local_nr: int
        Number of samples
    :param local_srate: float
        Sample rate in Hz (number of samples / time)
    :return: header_lst: list
        7 lines of scopy export information to be written to csv file
    """
    now = datetime.datetime.now()
    header_lst = [[";Scopy version", "48fb6a9"]]
    header_lst.append([";Exported on", now.strftime("%A %B %d/%m/%Y")])
    header_lst.append([";Device", "M2K"])
    header_lst.append([";Nr of samples", local_nr])
    header_lst.append([";Sample rate", local_srate])
    header_lst.append([";Tool", "Oscilloscope"])
    header_lst.append([";Additional Information", ""])
    return header_lst


def csv_eol():
    """
    Document end of line for csv data
    Turns out to be the same of Windows, Linux, and OSX
    :return: control string for use at end of each line while writing data to csv file
    """
    if os.name == "nt":
        return "\n"
    else:
        return "\n"


def main():
    # Number of samples
    nr = 1000
    # Time in seconds
    time = 1

    # Sampling rate 1000 hz / second
    srate = nr / time

    # Create sample count and time columns for CSV export
    s = np.fromiter((x for x in range(nr)), int)
    t = np.linspace(0, time, nr, endpoint=True)

    # Create, Plot, and Export square wave for FFT test
    # plot_title = '5 Hz Sqaure Wave: sample rate of 1000 Hz'
    # y = signal.square(2 * np.pi * 5 * t)
    # file_name = "data_1SquareWave.csv"

    # Create, Plot, and Export the sum of two sine waves for Butterworth Filter test
    plot_title = '10 Hz and 20 Hz Sine Waves: sample rate of 1000 Hz'
    y = np.sin(2*np.pi*10*t) + np.sin(2*np.pi*20*t)
    file_name = "data_2SineWaves.csv"

    file = open(file_name, 'w')

    # Export first 7 information lines formated in same way as an ADALM2000 Scopy Export to CSV file
    csv_heading = scopy_export_header(nr, srate)
    for i in range(len(csv_heading)):
        file.write("%s" % "," .join(map(str, csv_heading[i])))
        file.write(csv_eol())

    # Export data headings to CSV file
    csv_titles = ["Sample", "Time(S)", "CH1(V)"]
    file.write("%s" % "," .join(map(str, csv_titles)))
    file.write(csv_eol())

    # Export wave data to CSV file
    for i in range(nr):
        file.write("" .join((str(s[i]), ",", str(t[i]), ",", str(y[i]))))
        file.write(csv_eol())

    file.close()

    # Plot the wave signal
    plot.plot(t, y)
    # Give a title for the square wave plot
    plot.title(plot_title)
    # Give x axis label for the square wave plot
    plot.xlabel('Time')
    # Give y axis label for the square wave plot
    plot.ylabel('Amplitude')
    plot.grid(True, which='both')
    # Provide x axis and line color
    plot.axhline(y=0, color='k')
    # Set the max and min values for y axis
    plot.ylim(-2, 2)
    # Display the square wave drawn
    plot.show()


if __name__ == "__main__":
    main()
