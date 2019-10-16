# -*- coding: utf-8 -*-
"""
File: M2KCustomPlotFFT.py
This custom script uses ADALM2000 exported CSV data to plot FFT results.

v 1.01, August 13, 2019
    First release
v 1.10, October 12, 2019
        Add peak display feature, along with two control parameters: peak_cnt and min_peak_height
            - update constructor
            - update plot_custom_script() method
        Add intelligent display of frequency range for x-axis label in plot_custom_script()
        Add intelligent display of voltage range for y-axis label and legend in plot_custom_script()
        Eliminate labque titles from constructor, hard code them instead as:
            self.plot_title_1
            self.plot_title_2
        Eliminate self.headings_to_use, replace with just y_heading

Algorithm:
    Create the FFT from a given CSV data channel
    Prepare a plot of the results
    Include option to display largest peak information within plot (sorted by peak magnitude)

Author: Ron Fredericks, Ron@BiophysicsLab.com
License: MIT
Copyright 2019 Ron Fredericks, BiophysicsLab.com
See included license file (license.txt) or read it online: https://opensource.org/licenses/MIT
# --------------------------------------------------------------------------------------------

Main program refers to: M2KScopePlot.py

This script is completely contained within a class: CustomPlotScript(object):

    Attributes:
        values defined using __init__ constructor to customize the FFT plot
            self.y_heading
            self.n
            self.peak_cnt
            self.min_peak_height

        flag used to control whether custom script should be used or not
            self.is_custom_script

        data collected from CSV data file during execution of main program
            self.iplot_colors
            self.df_data
            self.info_dict
            self.headings

        Additional data copied from main program
            self.iplot_colors

        Additional strings used for FFT display in final lab report
            self.plot_title_1
            self.plot_title_2

    Methods:
        get_headings_to_use(self)
        get_is_custom_script(self)
        set_iplot_colors(self, iplot_colors)
        set_df_data(self, df_data)
        set_info_dict(self, info_dict)
        set_headings(self, headings)
        test_custom_plot(self)
        reduce_sample_array(signal_data, n)
        plot_custom_script(self)

Initiate the FFT plot script by creating an object within the main program (example):

    custom_script = CustomPlotScript('CH1(V)', 10, 4, 0.0)

    Where:
        'CH1(V)' is the y data heading from csv file to use for fft and plot
        10 reduces the data set by 10x to limit the x-axis frequency range plotted
        4 requests up to 4 peaks to feature within the plot/legend and final lab report
        0.0 requests all peaks found without any voltage limit (y-axis)

    Note:
        The peaks found are reported (labque and plot legend) with highest voltage first

"""
from scipy.fftpack import *
from scipy import signal
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from M2KScope.M2KScopePlotFncs import *


class CustomPlotScript(object):
    """
    A class used to add a custom plot to the end of the subplots created in the main program
    """

    def __init__(self, y_heading, n=1, peak_cnt=0, min_peak_height=0.0):
        """
        :param y_heading: str
                y-axis heading as found in csv data file
        :param n: positive integer
                Number of times to reduce FFT sampling frequency
                Larger n generates narrower frequency range for plotted fft
                When n=1 no sampling data will be removed
        :param peak_cnt: integer
                Maximum number of peaks to highlight (shown as vertical lines plus frequency, magnitude list in legend)
                Peaks are found using the scipy.signal.find_peak() function
                Number of peaks displayed will be the maximum of peaks found up to the number of peaks requested
                Note: -1 indicates all peaks should be displayed that meet min_peak_height limitation
        :param min_peak_height: float
                Use this parameter to skip peaks that are too small to be of interest
                The value corresponds to the FFT magnitude (in Volts). A value of .05 (Volts) for example
        """
        self.y_heading = y_heading.strip()
        self.n = int(n)
        self.peak_cnt = int(peak_cnt)
        self.min_peak_height = float(min_peak_height)

        # Titles packaged for labque display using headings_to_use() method
        self.plot_title_1 = "Custom FFT Plot using: "
        self.plot_title_2 = ", with dataset reduced by a factor of: "

        # Flag used to control custom script in main program
        self.is_custom_script = False

        # CSV data useful for custom scripting
        # ------------------------------------

        # List of colors to use for plotting
        #   example: iplot_colors = ['orange', 'magenta', 'green', 'blue', 'cyan', 'red', 'yellow', 'purple']
        self.iplot_colors = []

        # Pandas dataframe to hold imported csv column data, one row for each heading
        #
        #         Example using print(df_data)
        #
        #                 Sample     Time(S)     CH1(V)    CH2(V)     M1(V)
        #                 0          0 -0.004000 -0.003607 -0.009240  0.004883
        #                 1          1 -0.003999  0.001272 -0.004327  0.004883
        #                 2          2 -0.003998  0.004524  0.000585  0.003906
        #                 3          3 -0.003997  0.011029  0.007136  0.003906
        #                 ...      ...       ...       ...       ...       ...
        #                 7997    7997 0.003997  -0.023123 -0.028891  0.004883
        #                 7998    7998  0.003998 -0.021497 -0.022341  0.000000
        #                 7999    7999  0.003999 -0.010112 -0.014153  0.003906
        self.df_data = pd.DataFrame()

        # Dictionary of CSV info
        # Example:
        # info_dict = {
        #     'scopy': (';Scopy version', '48fb6a9')
        #     'export': (';Exported on', 'Wednesday July 24/07/2019')
        #     'device': (';Device', 'M2K')
        #     'samples': (';Nr of samples', '8000')
        #     'rate': (';Sample rate', '1.00E+06')
        #     'tool': (';Tool', 'Oscilloscope')
        # }
        self.info_dict = {}

        # List of df_data headings extracted from CSV file as strings
        # Example: Sample, Time(S), CH1(V), CH2(V)
        self.headings = []

        # plot data useful for custom scripting
        # ------------------------------------

        # List of colors to use for plotting
        #   Example:
        #       iplot_colors = ['orange', 'magenta', 'green', 'blue', 'cyan', 'red', 'yellow', 'purple']
        self.iplot_colors = []

        # reusable FFT peak display information for both plotting and labque display
        self.peak_title = ''
        self.flabel = []

    def get_headings_to_use(self):
        """
        Prepare a string for use by class LabQue() defined in M2MScopPlotTxtUI.py
            LabQue is used to print all useful data during the creation of plots
            Results are displayed on the screen and in text file next to plot images when saved

            Example:

                Recap of plot selections:
                    Program: M2KScopePlot: v1.01, August 2 2019
                    Plot CSV text file data generated by ADALM2000 Active Learning Module
                    Today's date: Thursday, August 22 2019
                    File selected: ./TestData/Lab2.csv
                    CSV data file generated on: Wednesday, July 24 2019
                    Scopy Version (48fb6a9): v1.06, May 24 2019
                    Plot title: M2K Oscilloscope [Nr of samples: 8000, Sample rate: 1e+06]
                    List of 'Y-axis' data channels selected to plot: CH1(V), CH2(V), M1(V)
                    Custom FFT Plot using: M1(V), with dataset reduced by a factor of: 200
                    Plot size selected: (8.0, 8.0) in inches
                    Plot data saved to file: ./TestData/Lab2.png
                    Message queue saved in file: ./TestData/Lab2.txt

        :return: formatted string containing plot_title_1 + y_heading + plot_title_2 + n
        """
        temp_str = self.plot_title_1
        temp_str += self.y_heading

        if self.n > 1:
            # include slice information if slicing actually occurs
            temp_str = temp_str + self.plot_title_2
            temp_str = temp_str + str(self.n)

        # Add FFT peak information to lab report - Recap of plot selections
        if self.peak_title:
            temp_str = temp_str + "\n\t" + self.peak_title + ":"
            for i in range(len(self.flabel)):
                temp_str = temp_str + "\n\t\t" + self.flabel[i]

        return temp_str

    def get_is_custom_script(self):
        """
        Flag used within main program to include a custom plot when True

        Methods used that involve is_custom_scipt flag
            test_custom_plot() -> sets or clears flag
            plot_custom_script() -> generates custom plot when flag is True

        :return: is_custom_script -> bool
            True indicates that all data is ready for custom plot
            False indicates no custom plot will be used
        """
        return self.is_custom_script

    def set_iplot_colors(self, iplot_colors):
        """
        Make a copy of the same custom plot color list as in the main program
        Select one of these list items to add color to custom script plot

        Used by method:
            plot_custom_script

        :param iplot_colors -> list of strings
        :return: None
        """
        self.iplot_colors = iplot_colors

    def set_df_data(self, df_data):
        """
        Make a copy of the same data extracted from ADALM2000 Scopy CSV data file used in the main program plots

        :param df_data: pandas dataframe
        :return: None
        """
        self.df_data = df_data

    def set_info_dict(self, info_dict):
        """
        Make a copy of the same info extracted from ADALM2000 Scopy CSV data file used in the main program
        Used to get sample rate in method custom_plot_script

        :param info_dict: dictionary
        :return: None
        """
        self.info_dict = info_dict

    def set_headings(self, headings):
        """
        Make a copy of the headings found in CSV export file during execution of the main plot program
        Used by method:
            test_custom_plot()

        Example:
            ['Sample', 'Time(S)', 'CH1(V)', 'CH2(V)', 'M1(V)']

        :param headings -> list of strings
        :return:
        """
        self.headings = headings

    def test_custom_plot(self):
        """
        Test for valid headings to be used in custom plot script
        Set is_custom_script to True if y_heading is found within headings
        Otherwise is_custom_script remains False
        """
        error_lst = ["\nCustom FFT Plot Script Error Report"]
        is_custom_script = True

        if self.y_heading:
            # custom script will not be used if y-axis heading is empty
            if self.y_heading not in self.headings[2:]:
                error_lst.append("\tERROR: Y-axis heading not found in headings list")
                is_custom_script = False
        else:
            error_lst.append("\tERROR: Y-axis heading is empty")
            is_custom_script = False

        if not is_custom_script:
            error_lst.append("\tHeadings available to use: " + str([item for item in self.headings[2:]]))
            for error_msg in error_lst:
                print(error_msg)
            input("\tPress any key to skip custom FFT plot script...")

        self.is_custom_script = is_custom_script

    @staticmethod
    def reduce_sample_array(signal_data, n):
        # n must be between 1 and signal_data size
        # signal_data size includes the number of samples * number of channels
        signal_data = signal_data[::n]
        return signal_data

    def plot_custom_script(self, grid_stack, grid_row):
        """
        Create a Magnitude vs Frequency plot for one of the columns of data captured in CSV data file
        Build logic to generate an FFT display using the following functions:
            self.reduce_sample_array() for frequency range
            scipy.fftpack -> fft() for y-axis
            scipy.fftpack -> fftfreq() for x-axis
            M2KScope.M2KScopePlotFncs ->
                                    compute_ticks() create a range of values defining grid ticks on a plot axis
        Main program plot loop sets up the plot using the following methods:
            plt.figure()
            plt.subplot()
        Prepare and execute the following plot parameters within this method:
            plt.plot()
            plt.xticks()
            plt.gca().set_xlim()
            plt.xticks()
            plt.title()
            plt.xlabel()
            plt.ylabel()
        Main program finally completes the custom plot using the following:
            plt.gca().xaxis.set_minor_locator()
            plt.gca().yaxis.set_minor_locator()
            plt.grid()
            plt.tight_layout()
            plt.savefig()
            plt.show()

        :return: None
        """
        # ref: https://stackoverflow.com/questions/48298724/fast-fourier-transform-on-motor-vibration-signal-in-python

        if not self.is_custom_script:
            # don't use this function if flag is false
            return

        # stack FFT plot in this figure vertically
        plt.subplot(grid_stack[grid_row, :])

        y_heading = self.y_heading

        # Reduce signal_data array size by a factor of n (used to reduce the frequency range)
        n = self.n
        updated_df_data = self.reduce_sample_array(self.df_data, n)

        # update sample rate and array size
        sample_rate = float(self.info_dict['rate'][1])/n
        array_size = updated_df_data[y_heading].size

        # Calculate y-axis magnitude scaled to same units as y-axis in heading2Use data (ie volts)
        yf = 2/array_size * fft(updated_df_data[y_heading].values)
        # Calculate x axis as frequency in Hz
        x = fftfreq(array_size, 1 / float(sample_rate))
        x_half = x[:x.size//2]

        freq_units, freq_multiplier = rescale_frequency(x_half)
        x_half = rescale_data(x_half, 10 ** freq_multiplier)

        y_half = abs(yf)[:array_size//2]
        engr_power_v = calculate_scale(y_half)
        y_half = rescale_data(y_half, 10**engr_power_v)

        plt.plot(x_half, y_half, color=self.iplot_colors[-1])

        # https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.find_peaks.html#scipy.signal.find_peaks
        if self.peak_cnt:
            peaks = signal.find_peaks(y_half, height=rescale_data(self.min_peak_height, 10**engr_power_v))[0]
            if peaks.size > 0:
                xhp = x_half[peaks]
                ayf = y_half[peaks]
                # Get indices that would sort voltage (magnitude) array.
                ayf_as = np.argsort(ayf)
                max_peaks = xhp.size
                # Determine how many FFT peaks to display (all or limited from class constructor input)
                if self.peak_cnt < 0:
                    peak_cnt = max_peaks
                else:
                    peak_cnt = min(max_peaks, self.peak_cnt)
                if peak_cnt == 1:
                    self.peak_title = 'FFT Peak Value'
                else:
                    self.peak_title = 'Largest FFT Peak Values'
                for i in range(peak_cnt):
                    i_ptr = ayf_as[len(ayf_as)-i-1]
                    # cycle through colors in self.iplot_colors[] but skip FFT plot color self.iplot_colors[-1]
                    icolor_ptr = (-1 - i) % (len(self.iplot_colors)-1)
                    self.flabel.append("{:.2f} {}, {:.2f} {}".format(xhp[i_ptr], freq_units,  ayf[i_ptr],
                                                                     adjust_voltage_heading('V', engr_power_v)))
                    plt.plot((xhp[i_ptr], xhp[i_ptr]), (0.0, ayf[i_ptr]), color=self.iplot_colors[icolor_ptr],
                             dashes=[2, 2], label=self.flabel[i])
                plt.legend(loc='upper right', title=self.peak_title)

        # Initialize x-axis scale variables used to calculate 10 major ticks: like an oscilloscope
        myrange = compute_ticks(x_half, 10)
        # Append one delta step to myrange to get 10 oscilloscope-like divisions (not just 10 ticks)
        if len(myrange) > 1:
            myrange = np.append(myrange, [myrange[len(myrange)-1]+(myrange[1]-myrange[0])])

        # Complete the display of x-axis
        # https://matplotlib.org/3.1.1/api/_as_gen/matplotlib.pyplot.xticks.html
        plt.xticks(myrange)
        plt.gca().set_xlim(myrange[0], myrange[len(myrange)-1])
        plt.xticks(rotation=45)
        plt.xlabel('Frequency (' + freq_units + ')')

        # Complete the display of y-axis
        plt.ylabel(adjust_voltage_heading(self.y_heading, engr_power_v), color=self.iplot_colors[-1])

        # Prepare custom plot title
        plt.title("Magnitude vs Spectrum")
